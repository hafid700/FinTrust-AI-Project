"""Mise à jour A6b : checkpoint FedAvg + paquet d'explication pour la Personne B.

Usage (à la racine du dépôt fintrust-ai) :   python patch_A6b.py
Idempotent : peut être relancé sans danger. S'arrête avec un message clair si un fichier
n'a pas la forme attendue (dans ce cas, envoyer le fichier concerné).
"""
from pathlib import Path
import sys

ROOT = Path(".")


def read(p):
    return (ROOT / p).read_text(encoding="utf-8")


def write(p, text):
    path = ROOT / p
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def patch(p, old, new, marker):
    t = read(p)
    if marker in t:
        print(f"  = {p} : déjà à jour ({marker})")
        return
    if old not in t:
        sys.exit(f"ERREUR : motif introuvable dans {p} :\n{old}\n-> envoie-moi ce fichier.")
    write(p, t.replace(old, new, 1))
    print(f"  + {p} : modifié")


print("1) gnn.py : méthode embed()")
patch("src/detection/gnn.py",
      "    def forward(self, num_nodes: int, edge_index, edge_attr, sel):",
      '''    def embed(self, num_nodes: int, edge_index, edge_attr):
        """Embeddings de noeuds (contexte réseau) après message passing."""
        src, dst = edge_index
        deg = torch.stack([torch.bincount(dst, minlength=num_nodes),
                           torch.bincount(src, minlength=num_nodes)], dim=1).to(edge_attr.dtype)
        h = F.relu(self.node_in(torch.log1p(deg)))
        for layer in self.layers:
            h = layer(h, edge_index, edge_attr)
        return h

    def forward(self, num_nodes: int, edge_index, edge_attr, sel):''',
      "def embed(self")

print("2) fed_data.py : noms des features")
patch("src/detection/fed_data.py",
      "    X_base, _ = build_edge_features(df, split)",
      "    X_base, base_names = build_edge_features(df, split)", "base_names = build_edge_features")
patch("src/detection/fed_data.py",
      '        "n_edge_features": int(views[0].edge_attr.shape[1]),\n',
      '        "n_edge_features": int(views[0].edge_attr.shape[1]),\n        "feature_names": base_names + gnames,\n',
      '"feature_names": base_names + gnames')

print("3) federated.py : sauvegarde du checkpoint")
patch("src/detection/federated.py",
      'pos_weight_power=0.5, seed=42, out_dir="reports/a4", device=None):',
      'pos_weight_power=0.5, seed=42, out_dir="reports/a4", device=None, ckpt_dir=None):', "ckpt_dir=None")
patch("src/detection/federated.py",
      "        gmodel.load_state_dict(best_state)\n        comm_mb",
      '''        gmodel.load_state_dict(best_state)
        if ckpt_dir:                                              # petit fichier (~200 Ko) : peut être commité
            Path(ckpt_dir).mkdir(parents=True, exist_ok=True)
            torch.save({"state_dict": {k: v.detach().cpu() for k, v in best_state.items()},
                        "edge_dim": edge_dim, "hidden": hidden, "layers": layers,
                        "feature_names": info["feature_names"], "partition": partition,
                        "n_clients": n_clients, "seed": seed, "pos_weight": float(pw), "n_params": n_params},
                       Path(ckpt_dir) / f"{tag}_fedavg_seed{seed}.pt")
        comm_mb''', "torch.save({")
patch("src/detection/federated.py",
      '    ap.add_argument("--seed", type=int, default=42)\n    a = ap.parse_args()\n',
      '    ap.add_argument("--seed", type=int, default=42)\n    ap.add_argument("--ckpt-dir", default="checkpoints")\n    a = ap.parse_args()\n',
      '"--ckpt-dir"')
patch("src/detection/federated.py",
      "seed=a.seed, out_dir=a.out)", "seed=a.seed, out_dir=a.out,\n                   ckpt_dir=a.ckpt_dir)", "ckpt_dir=a.ckpt_dir")

print("4) nouveaux fichiers")
write("src/detection/fedavg_head.py", r'''"""Tête de classification du modèle FedAvg, utilisable SANS graphe ni données (pour SHAP / Captum).

Le modèle calcule  logit = tête([h_src, h_dst, x])  où
  x      = 50 features de la transaction (28 de base + 22 features de graphe causales) ;
  h_src, h_dst = embeddings des deux comptes (contexte réseau, issus du message passing).
Le paquet d'explication (`export_explain_bundle.py`) fournit h_src, h_dst et x pour chaque alerte.
"""
from __future__ import annotations

import numpy as np
import torch

from src.detection.gnn import EdgeGNN


def load_head(ckpt_path: str):
    """Retourne (tête nn.Module en mode eval, noms des features, dimension des embeddings)."""
    ck = torch.load(ckpt_path, map_location="cpu", weights_only=True)
    model = EdgeGNN(ck["edge_dim"], ck["hidden"], ck["layers"])
    model.load_state_dict(ck["state_dict"])
    model.eval()
    return model.cls, ck["feature_names"], ck["hidden"]


@torch.no_grad()
def head_logit(head, h_src: np.ndarray, h_dst: np.ndarray, x: np.ndarray) -> np.ndarray:
    """Logits pour des tableaux (n, hidden), (n, hidden), (n, n_features)."""
    z = torch.from_numpy(np.concatenate([h_src, h_dst, x], axis=1).astype(np.float32))
    return head(z).squeeze(-1).numpy()
''')

write("src/detection/export_explain_bundle.py", r'''"""A6b - Paquet d'explication pour la Personne B (SHAP / Integrated Gradients).

Pour chaque alerte : embeddings h_src et h_dst (contexte réseau fixé par le GNN), features x,
logit du modèle. + un jeu de fond (background) de transactions de test pour SHAP.
Vérifie que le logit recalculé à partir du paquet égale celui du fichier de scores.

    python -m src.detection.export_explain_bundle
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from src.common.alert import load_alerts
from src.detection.fed_data import build_client_views
from src.detection.federated import ClientData
from src.detection.gnn import EdgeGNN


@torch.no_grad()
def build_bundle(df, ckpt_path, tx_ids, n_background=500, seed=42, device="cpu"):
    ck = torch.load(ckpt_path, map_location=device, weights_only=True)
    model = EdgeGNN(ck["edge_dim"], ck["hidden"], ck["layers"]).to(device)
    model.load_state_dict(ck["state_dict"])
    model.eval()
    views, info = build_client_views(df, ck["n_clients"], ck["partition"], ck["seed"])
    if info["feature_names"] != ck["feature_names"]:
        raise ValueError("Les features reconstruites ne correspondent pas au checkpoint (données différentes ?).")

    wanted = np.asarray(tx_ids, dtype=np.int64)
    rng = np.random.default_rng(seed)
    cols = ("tx_id", "client", "h_src", "h_dst", "x", "logit")
    alert, bg = {c: [] for c in cols}, {c: [] for c in cols}
    for v in views:
        cd = ClientData(v, device)
        ei, ea, sel, _, tx = cd.graph(2)                    # graphe complet, arêtes de test possédées
        if len(sel) == 0:
            continue
        h = model.embed(cd.n, ei, ea)
        hs, hd, x = h[ei[0][sel]], h[ei[1][sel]], ea[sel]
        logit = model.cls(torch.cat([hs, hd, x], dim=1)).squeeze(-1)
        tx_np = tx.cpu().numpy()
        take_alert = np.isin(tx_np, wanted)
        rest = np.where(~take_alert)[0]
        take_bg = rest[rng.choice(len(rest), min(len(rest), n_background // len(views) + 1), replace=False)]
        for store, idx in ((alert, np.where(take_alert)[0]), (bg, take_bg)):
            it = torch.as_tensor(idx, dtype=torch.long, device=hs.device)
            store["tx_id"].append(tx_np[idx])
            store["client"].append(np.full(len(idx), v.client))
            store["h_src"].append(hs[it].cpu().numpy())
            store["h_dst"].append(hd[it].cpu().numpy())
            store["x"].append(x[it].cpu().numpy())
            store["logit"].append(logit[it].cpu().numpy())
    cat = lambda d: {k: np.concatenate(v) for k, v in d.items()}
    return cat(alert), cat(bg), ck


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", default="checkpoints/fed3_balanced_fedavg_seed42.pt")
    ap.add_argument("--parquet", default="data/processed/hi_small_sub.parquet")
    ap.add_argument("--alerts", default="reports/a6/alerts_fedavg.jsonl")
    ap.add_argument("--scores", default="reports/a4/fed3_balanced_fedavg_scores.npz")
    ap.add_argument("--out", default="reports/a6")
    a = ap.parse_args()

    df = pd.read_parquet(a.parquet)
    if not df["timestamp"].is_monotonic_increasing:
        df = df.sort_values("timestamp", kind="stable").reset_index(drop=True)
    tx_ids = [al.tx_id for al in load_alerts(a.alerts)]
    alert, bg, ck = build_bundle(df, a.ckpt, tx_ids)

    s = np.load(a.scores)
    ref = dict(zip(s["test_tx_id"], s["test_logit"]))
    dev = float(np.max(np.abs(alert["logit"] - np.array([ref[t] for t in alert["tx_id"]]))))
    print(f"alertes retrouvées : {len(alert['tx_id'])}/{len(tx_ids)} | écart max de logit vs scores : {dev:.2e}")
    if len(alert["tx_id"]) != len(tx_ids) or dev > 1e-3:
        print("ATTENTION : le checkpoint ne correspond pas au fichier de scores / aux alertes. "
              "Régénérez scores, alertes et paquet depuis le même entraînement.")

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out / "explain_bundle_fedavg.npz", feature_names=np.array(ck["feature_names"]),
                        hidden=ck["hidden"], **alert, **{f"bg_{k}": v for k, v in bg.items()})
    (out / "feature_names.json").write_text(json.dumps(ck["feature_names"], indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
''')

write("docs/EXPLICATION_FEDAVG.md", r'''# Expliquer une alerte FedAvg (pour la partie B)

Fichiers fournis par A : `checkpoints/fed3_balanced_fedavg_seed42.pt` (poids, ~200 Ko) et
`reports/a6/explain_bundle_fedavg.npz`.

Le modèle calcule `logit = tête([h_src, h_dst, x])` :
- `x` : 50 features de la transaction (noms dans `feature_names`) dont 22 features de graphe causales ;
- `h_src`, `h_dst` : embeddings des deux comptes (contexte réseau du GNN, 64 dimensions chacun).

On explique donc la contribution des 50 features de `x`, le contexte réseau (embeddings) étant fixé.
C'est une explication « au niveau de la tête » : elle ne passe pas par GNNExplainer (qui suppose les
couches PyG standard), mais SHAP et Integrated Gradients s'appliquent directement.

## Exemple KernelSHAP (à adapter ; non testé)
```python
import numpy as np, shap
from src.detection.fedavg_head import load_head, head_logit

b = np.load("reports/a6/explain_bundle_fedavg.npz")
head, names, _ = load_head("checkpoints/fed3_balanced_fedavg_seed42.pt")
i = 0                                                # une alerte
hs, hd, x = b["h_src"][i:i+1], b["h_dst"][i:i+1], b["x"][i:i+1]
f = lambda X: head_logit(head, np.repeat(hs, len(X), 0), np.repeat(hd, len(X), 0), X)
expl = shap.KernelExplainer(f, b["bg_x"][:100])
sv = expl.shap_values(x, nsamples=200)[0]
top = sorted(zip(names, sv), key=lambda t: -abs(t[1]))[:5]    # -> top_features de l'alerte
```
Vérification utile : `f(x)` doit égaler `b["logit"][i]`.

## Integrated Gradients (Captum)
La tête est un `nn.Sequential` : on peut utiliser `captum.attr.IntegratedGradients` sur l'entrée
`z = [h_src, h_dst, x]` (178 dims), puis ne garder que les 50 dernières composantes (ou regrouper
les 128 premières en « contexte réseau »).
''')

print("5) test, .gitignore, README")
if "test_explain_bundle_matches_scores" not in read("tests/test_federated.py"):
    write("tests/test_federated.py", read("tests/test_federated.py").rstrip() + "\n\n\n" + r'''def test_explain_bundle_matches_scores(fake_csv, tmp_path):
    pytest.importorskip("torch")
    from src.detection.export_explain_bundle import build_bundle
    from src.detection.federated import run_experiment
    from src.detection.fedavg_head import head_logit, load_head

    df = load_transactions(str(fake_csv))
    run_experiment(df, scenarios=("fedavg",), rounds=2, local_epochs=1, hidden=8, layers=1, patience=5,
                   out_dir=str(tmp_path), device="cpu", ckpt_dir=str(tmp_path / "ck"))
    ckpt = str(tmp_path / "ck" / "fed3_balanced_fedavg_seed42.pt")
    sc = np.load(tmp_path / "fed3_balanced_fedavg_scores.npz")
    wanted = sc["test_tx_id"][:25]
    alert, bg, ck = build_bundle(df, ckpt, wanted, n_background=30)
    ref = dict(zip(sc["test_tx_id"], sc["test_logit"]))
    assert len(alert["tx_id"]) == len(wanted)
    assert np.max(np.abs(alert["logit"] - np.array([ref[t] for t in alert["tx_id"]]))) < 1e-4
    assert alert["x"].shape[1] == len(ck["feature_names"]) and alert["h_src"].shape[1] == ck["hidden"]
    assert len(bg["tx_id"]) > 0
    head, names, _ = load_head(ckpt)
    rec = head_logit(head, alert["h_src"], alert["h_dst"], alert["x"])
    assert np.max(np.abs(rec - alert["logit"])) < 1e-4
''')
    print("  + tests/test_federated.py : test ajouté")

gi = ROOT / ".gitignore"
g = gi.read_text(encoding="utf-8") if gi.exists() else ""
if "!checkpoints/" not in g:
    g = g.replace("*.pt\n", "*.pt\n!checkpoints/*.pt\n", 1) if "*.pt\n" in g else g + "\n!checkpoints/*.pt\n"
    gi.write_text(g, encoding="utf-8")
    print("  + .gitignore : checkpoints/*.pt autorisés")

rd = ROOT / "README.md"
if rd.exists() and "A6b" not in rd.read_text(encoding="utf-8"):
    rd.write_text(rd.read_text(encoding="utf-8").rstrip() + "\n- A6b : `checkpoints/` (poids FedAvg, commités) + "
                  "`reports/a6/explain_bundle_fedavg.npz` pour SHAP/IG (voir `docs/EXPLICATION_FEDAVG.md`).\n",
                  encoding="utf-8")
print("Terminé.")