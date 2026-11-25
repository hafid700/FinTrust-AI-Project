#!/usr/bin/env python3
"""B5 (partie 2) - Explication des alertes du modèle FedAvg de A : quelles features ont fait monter le score ?

Le modèle de A calcule  logit = tête([h_src, h_dst, x])  avec
    x      : 50 features de la transaction (noms dans le checkpoint),
    h_src, h_dst : embeddings des deux comptes (contexte réseau du GNN, 64 dims chacun).
GNNExplainer n'est pas utilisable (message passing sur mesure) : on explique la TÊTE, avec le
contexte réseau FIXÉ (consigne de A), par deux méthodes qui doivent donner la même réponse :

  * Integrated Gradients moyennés sur K références de fond ("expected gradients") : déterministe,
    rapide, exact par construction pour l'additivité (somme des attributions = f(x) - f(fond)) ;
  * KernelSHAP (bibliothèque `shap`) : référence, plus lente et bruitée, utilisée pour VALIDER.

Les attributions sont en unités de LOGIT, signées : positif = a poussé vers « illicite ».
Elles sont relatives à un fond (501 transactions de fond fournies par A, 2,5 % d'illicites environ).
Les 50 features sont regroupées pour la lecture : les variables « one-hot » `payment_format_*` et
`payment_currency_*` forment chacune un groupe (la somme des attributions d'un groupe est exacte).

Le module n'a besoin que de torch et numpy (+ shap pour la validation) : il relit le checkpoint
sans importer le code de A.

    python audit/explain.py --bundle reports/a6/explain_bundle_fedavg.npz \
        --ckpt checkpoints/fed3_balanced_fedavg_seed42.pt --alerts audit/results/b5/alerts_calibrated.jsonl \
        --out audit/results/b5
"""
import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn

FIXED = "contexte réseau fixé (embeddings des comptes)"


# --- Chargement de la tête ---------------------------------------------------

def load_head(ckpt_path):
    """Reconstruit la tête (178 -> 64 -> 1) depuis les poids `cls.*` du checkpoint de A."""
    ck = torch.load(ckpt_path, map_location="cpu", weights_only=True)
    sd = {k[4:]: v for k, v in ck["state_dict"].items() if k.startswith("cls.")}
    w0, w3 = sd["0.weight"], sd["3.weight"]
    head = nn.Sequential(nn.Linear(w0.shape[1], w0.shape[0]), nn.ReLU(), nn.Dropout(0.2),
                         nn.Linear(w3.shape[1], w3.shape[0]))
    head.load_state_dict(sd)
    head.eval()
    for p in head.parameters():
        p.requires_grad_(False)
    return head, list(ck["feature_names"]), int(ck["hidden"])


@torch.no_grad()
def head_logit(head, hs, hd, x):
    z = torch.as_tensor(np.concatenate([hs, hd, x], axis=1), dtype=torch.float32)
    return head(z).squeeze(-1).numpy()


def feature_groups(names):
    """{groupe: [indices]} : one-hot de format et de devise regroupés, le reste individuel."""
    groups = {}
    for i, n in enumerate(names):
        if n.startswith("payment_format_"):
            g = "payment_format"
        elif n.startswith("payment_currency_"):
            g = "payment_currency"
        else:
            g = n
        groups.setdefault(g, []).append(i)
    return groups


# --- Integrated Gradients moyennés sur un fond --------------------------------

def expected_ig(head, hs, hd, x, bg_x, steps: int = 32, chunk: int = 16):
    """Attributions (n, n_features) de f(x) = tête([hs, hd, x]) par rapport aux K références `bg_x`.

    attr_j = moyenne_k[ (x_j - b_kj) * moyenne_s dF/dx_j (b_k + s/S (x - b_k)) ]
    Complétude : sum_j attr_j = f(x) - moyenne_k f(b_k)   (contexte réseau de l'alerte fixé).
    Intégrale par la règle du point milieu à `steps` pas.
    """
    n, d = x.shape
    K = len(bg_x)
    bg = torch.as_tensor(bg_x, dtype=torch.float32)
    alphas = (torch.arange(steps, dtype=torch.float32) + 0.5) / steps
    out = np.zeros((n, d), dtype=np.float64)
    for s in range(0, n, chunk):
        e = min(s + chunk, n)
        xb = torch.as_tensor(x[s:e], dtype=torch.float32)          # (m, d)
        m = e - s
        # chemin : (m, K, S, d)
        path = bg[None, :, None, :] + alphas[None, None, :, None] * (xb[:, None, None, :] - bg[None, :, None, :])
        path = path.reshape(-1, d).clone().requires_grad_(True)
        h = torch.as_tensor(np.concatenate([hs[s:e], hd[s:e]], axis=1), dtype=torch.float32)
        h = h[:, None, None, :].expand(m, K, steps, h.shape[1]).reshape(-1, h.shape[1])
        f = head(torch.cat([h, path], dim=1)).sum()
        (g,) = torch.autograd.grad(f, path)
        g = g.reshape(m, K, steps, d).mean(2)                      # (m, K, d)
        attr = ((xb[:, None, :] - bg[None]) * g).mean(1)           # (m, d)
        out[s:e] = attr.numpy()
    return out


def base_value(head, hs, hd, bg_x):
    """E_k f(b_k) avec le contexte de chaque alerte : valeur de référence de l'explication."""
    n, K = len(hs), len(bg_x)
    out = np.zeros(n)
    for i in range(n):
        out[i] = head_logit(head, np.repeat(hs[i:i + 1], K, 0), np.repeat(hd[i:i + 1], K, 0), bg_x).mean()
    return out


# --- Validation par KernelSHAP ------------------------------------------------

def kernel_shap(head, hs, hd, x, bg_x, nsamples: int = 1000, seed: int = 0):
    """Attributions KernelSHAP (bibliothèque shap) pour chaque ligne de x ; fond = bg_x."""
    import shap

    out = np.zeros(x.shape, dtype=np.float64)
    np.random.seed(seed)
    for i in range(len(x)):
        f = lambda X, i=i: head_logit(head, np.repeat(hs[i:i + 1], len(X), 0),
                                      np.repeat(hd[i:i + 1], len(X), 0), np.asarray(X, np.float32))
        ex = shap.KernelExplainer(f, bg_x)
        out[i] = ex.shap_values(x[i:i + 1], nsamples=nsamples, silent=True)[0]
    return out


# --- Sorties lisibles ---------------------------------------------------------

def group_attr(attr, groups):
    """(n, d) -> (n, G) en sommant les attributions d'un groupe ; renvoie aussi les noms."""
    names = list(groups)
    return np.stack([attr[:, groups[g]].sum(1) for g in names], axis=1), names


def top_features(gattr_row, gnames, k: int = 3):
    """k groupes d'attribution absolue maximale -> [[nom, poids normalisé]], signes à part.

    poids = |attribution| / somme des |attributions| (sur tous les groupes), dans [0, 1],
    comme le champ `top_features` du contrat d'interface. `signe` : +1 vers illicite, -1 vers licite.
    """
    tot = np.abs(gattr_row).sum() + 1e-12
    order = np.argsort(-np.abs(gattr_row))[:k]
    return ([[gnames[j], round(float(abs(gattr_row[j]) / tot), 4)] for j in order],
            [int(np.sign(gattr_row[j])) for j in order])


# --- Évaluation de la fidélité -------------------------------------------------

def deletion_test(head, hs, hd, x, attr_groups, groups, gnames, bg_mean, ks=(1, 3, 5), seed=0):
    """Si on remet à la valeur moyenne du fond les k groupes jugés les plus importants (poussant vers
    « illicite »), de combien le logit baisse-t-il, comparé à k groupes tirés au hasard ?
    Une bonne explication fait baisser le logit nettement plus que le hasard."""
    rng = np.random.default_rng(seed)
    base = head_logit(head, hs, hd, x)
    res = {}
    for k in ks:
        xt, xr = x.copy(), x.copy()
        for i in range(len(x)):
            top = np.argsort(-attr_groups[i])[:k]                 # plus forte poussée vers illicite
            rnd = rng.choice(len(gnames), size=k, replace=False)
            for j in top:
                xt[i, groups[gnames[j]]] = bg_mean[groups[gnames[j]]]
            for j in rnd:
                xr[i, groups[gnames[j]]] = bg_mean[groups[gnames[j]]]
        res[k] = {"drop_top": float(np.mean(base - head_logit(head, hs, hd, xt))),
                  "drop_random": float(np.mean(base - head_logit(head, hs, hd, xr)))}
    return res


def spearman(a, b):
    ra = np.argsort(np.argsort(a))
    rb = np.argsort(np.argsort(b))
    return float(np.corrcoef(ra, rb)[0, 1])


# --- Orchestration -----------------------------------------------------------

def run(bundle_path, ckpt_path, out_dir, alerts_path=None, k_top: int = 3, n_base: int = 100,
        steps: int = 32, n_check: int = 60, shap_samples: int = 1000, seed: int = 42, skip_shap=False):
    b = np.load(bundle_path, allow_pickle=True)
    head, names, _ = load_head(ckpt_path)
    assert list(map(str, b["feature_names"])) == names, "noms de features différents du checkpoint"
    hs, hd, x, logit = b["h_src"], b["h_dst"], b["x"], b["logit"]
    tx = b["tx_id"].tolist()
    groups = feature_groups(names)

    rng = np.random.default_rng(seed)
    bg_idx = rng.choice(len(b["bg_x"]), size=min(n_base, len(b["bg_x"])), replace=False)
    bg = b["bg_x"][bg_idx]

    summary = {"n_alerts": len(tx), "n_features": len(names), "n_groups": len(groups),
               "background": {"n": int(len(bg)), "mean_p_illicit": float(
                   (1 / (1 + np.exp(-b["bg_logit"][bg_idx]))).mean())},
               "method": "Integrated Gradients moyennés sur le fond (contexte réseau fixé)"}
    # 1. la tête reconstruite reproduit les logits de A
    summary["head_fidelity_max_abs_error"] = float(np.abs(head_logit(head, hs, hd, x) - logit).max())

    # 2. attributions pour toutes les alertes
    t0 = time.time()
    attr = expected_ig(head, hs, hd, x, bg, steps=steps)
    summary["ig_seconds"] = round(time.time() - t0, 1)
    base = base_value(head, hs, hd, bg)
    gap = (logit - base) - attr.sum(1)
    summary["completeness"] = {"max_abs_error": float(np.abs(gap).max()),
                               "mean_abs_error": float(np.abs(gap).mean()),
                               "mean_logit_minus_base": float((logit - base).mean())}
    gattr, gnames = group_attr(attr, groups)

    # 3. validation croisée avec KernelSHAP sur un échantillon
    if not skip_shap:
        sel = rng.choice(len(tx), size=min(n_check, len(tx)), replace=False)
        t0 = time.time()
        ks = kernel_shap(head, hs[sel], hd[sel], x[sel], bg, nsamples=shap_samples, seed=seed)
        kg, _ = group_attr(ks, groups)
        top3_overlap = [len(set(np.argsort(-np.abs(kg[i]))[:3]) & set(np.argsort(-np.abs(gattr[sel][i]))[:3])) / 3
                        for i in range(len(sel))]
        top1_same = [int(np.argmax(np.abs(kg[i])) == np.argmax(np.abs(gattr[sel][i]))) for i in range(len(sel))]
        summary["vs_kernelshap"] = {
            "n_alerts_checked": int(len(sel)), "shap_samples": shap_samples,
            "spearman_per_alert_mean": float(np.mean([spearman(kg[i], gattr[sel][i]) for i in range(len(sel))])),
            "top3_overlap_mean": float(np.mean(top3_overlap)),
            "top1_same_rate": float(np.mean(top1_same)),
            "mean_abs_diff_logit_units": float(np.abs(kg - gattr[sel]).mean()),
            "kernelshap_seconds": round(time.time() - t0, 1)}

    # 4. fidélité : test de suppression
    bg_mean = bg.mean(0)
    sub = rng.choice(len(tx), size=min(500, len(tx)), replace=False)
    summary["deletion_test_mean_logit_drop"] = deletion_test(head, hs[sub], hd[sub], x[sub], gattr[sub],
                                                             groups, gnames, bg_mean)

    # 5. quelle part du logit vient du contexte réseau ? (IG sur les 178 entrées, références jointes)
    summary["context_share"] = context_share(head, hs[sub[:200]], hd[sub[:200]], x[sub[:200]], b, bg_idx, steps)

    # 6. fréquence des features dans le top-k
    from collections import Counter
    cnt = Counter()
    for i in range(len(tx)):
        t, _ = top_features(gattr[i], gnames, k_top)
        cnt.update(n for n, _ in t)
    summary["top_feature_frequency_%"] = {n: round(100 * c / len(tx), 1) for n, c in cnt.most_common(12)}

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out / "attributions_fedavg.npz", tx_id=np.array(tx), group_names=np.array(gnames),
                        group_attr=gattr.astype(np.float32), base=base.astype(np.float32), logit=logit)
    plot_explanations(gattr, gnames, logit, base, out / "explanations_overview.png")
    if alerts_path:
        alerts = [json.loads(l) for l in open(alerts_path, encoding="utf-8") if l.strip()]
        pos = {t: i for i, t in enumerate(tx)}
        miss = 0
        with open(out / "alerts_explained.jsonl", "w", encoding="utf-8") as f:
            for a in alerts:
                i = pos.get(a["tx_id"])
                if i is None:
                    miss += 1
                    continue
                t, sg = top_features(gattr[i], gnames, k_top)
                a["top_features"] = t
                a["explanation"] = {"method": "integrated_gradients_bg", "unit": "logit", "signs": sg,
                                    "base_logit": float(base[i]), "logit": float(logit[i]),
                                    "context": FIXED}
                f.write(json.dumps(a, ensure_ascii=False) + "\n")
        summary["alerts_without_attribution"] = miss
    (out / "explain_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return summary


def plot_explanations(gattr, gnames, logit, base, path, top=12):
    """Gauche : importance globale (moyenne des |attributions|). Droite : une alerte (attributions signées)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    imp = np.abs(gattr).mean(0)
    o = np.argsort(-imp)[:top][::-1]
    i = int(np.argmax(logit))                      # alerte la plus confiante du modèle, à titre d'exemple
    oi = np.argsort(-np.abs(gattr[i]))[:8][::-1]
    fig, ax = plt.subplots(1, 2, figsize=(13, 4.8))
    ax[0].barh([gnames[j] for j in o], imp[o], color="#1f77b4")
    ax[0].set_title(f"Importance globale ({len(gattr)} alertes)")
    ax[0].set_xlabel("moyenne de |attribution| (unités de logit)")
    ax[1].barh([gnames[j] for j in oi], gattr[i, oi], color=["#d62728" if v > 0 else "#2ca02c" for v in gattr[i, oi]])
    ax[1].axvline(0, color="k", lw=.8)
    ax[1].set_title(f"Une alerte : logit {logit[i]:.2f} contre fond {base[i]:.2f}")
    ax[1].set_xlabel("attribution (rouge : vers illicite, vert : vers licite)")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def context_share(head, hs, hd, x, b, bg_idx, steps):
    """Part de |attribution| portée par : features de la transaction / contexte émetteur / contexte destinataire."""
    d = x.shape[1]
    Z = np.concatenate([hs, hd, x], axis=1)
    BG = np.concatenate([b["bg_h_src"][bg_idx], b["bg_h_dst"][bg_idx], b["bg_x"][bg_idx]], axis=1)
    K = len(BG)
    bg = torch.as_tensor(BG, dtype=torch.float32)
    alphas = (torch.arange(steps, dtype=torch.float32) + 0.5) / steps
    shares = []
    for i in range(len(Z)):
        zi = torch.as_tensor(Z[i], dtype=torch.float32)
        path = (bg[:, None, :] + alphas[None, :, None] * (zi[None, None, :] - bg[:, None, :])).reshape(-1, Z.shape[1])
        path = path.clone().requires_grad_(True)
        (g,) = torch.autograd.grad(head(path).sum(), path)
        attr = ((zi[None] - bg) * g.reshape(K, steps, -1).mean(1)).mean(0).numpy()
        h = hs.shape[1]
        parts = np.array([np.abs(attr[:h]).sum(), np.abs(attr[h:2 * h]).sum(), np.abs(attr[2 * h:]).sum()])
        shares.append(parts / parts.sum())
    s = np.mean(shares, axis=0)
    return {"n_alerts": int(len(Z)), "transaction_features": float(s[2]),
            "context_source_account": float(s[0]), "context_destination_account": float(s[1]),
            "note": "part de la somme des |attributions| (références jointes embeddings + features)"}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--bundle", required=True)
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--alerts", default=None)
    ap.add_argument("--out", default="audit/results/b5")
    ap.add_argument("--top", type=int, default=3)
    ap.add_argument("--n-base", type=int, default=100)
    ap.add_argument("--steps", type=int, default=32)
    ap.add_argument("--n-check", type=int, default=60)
    ap.add_argument("--skip-shap", action="store_true")
    a = ap.parse_args()
    s = run(a.bundle, a.ckpt, a.out, a.alerts, a.top, a.n_base, a.steps, a.n_check, skip_shap=a.skip_shap)
    print(json.dumps({k: v for k, v in s.items()}, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
