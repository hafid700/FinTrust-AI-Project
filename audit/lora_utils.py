#!/usr/bin/env python3
"""B4 - Fonctions communes au fine-tuning LoRA et à son évaluation.

Ce module contient toute la logique de B4 ; le notebook Colab
(notebooks/B4_lora_finetuning.ipynb) ne fait que l'orchestrer. Les imports
lourds (torch, peft) sont faits à l'intérieur des fonctions : le module peut
être importé, et ses fonctions de texte testées, sans GPU.

Contenu :
  1. Prompts            : même gabarit pour l'entraînement et l'inférence
  2. Encodage           : tokenisation + masquage (la perte ne porte que sur le rapport)
  3. LoRA               : application du LoRA, boucle d'entraînement, comptage des paramètres
  4. Génération         : génération par lots, déterministe (greedy)
  5. RAG                : construction du contexte réglementaire d'une alerte
  6. Métriques          : exactitude des faits, structure, citations
"""
import json
import math
import random
import re
import time
from pathlib import Path

try:
    from report_checks import check_report
    from build_instruction_dataset import INSTRUCTION
except ImportError:  # import depuis la racine du dépôt (Colab)
    from audit.report_checks import check_report
    from audit.build_instruction_dataset import INSTRUCTION

SYSTEM_PROMPT = (
    "Tu es un assistant spécialisé en conformité bancaire "
    "(lutte contre le blanchiment de capitaux et le financement du terrorisme)."
)

SECTIONS = [
    "1. Résumé",
    "2. Schéma détecté",
    "3. Facteurs explicatifs",
    "4. Références réglementaires",
    "5. Recommandations",
]

# Baseline « prompt seul » : on donne au modèle de base TOUT ce qu'un bon prompt
# peut apporter (structure, règles). Sans cela, la comparaison avec le LoRA
# serait un homme de paille : on mesure ce que le fine-tuning apporte EN PLUS
# d'un prompt soigné.
PROMPT_ONLY_INSTRUCTION = (
    INSTRUCTION
    + "\n\nStructure attendue (respecte exactement ces intitulés) :\n"
    + "RAPPORT D'AUDIT — Transaction <tx_id>\n"
    + "\n".join(SECTIONS)
    + "\n\nRègles : écris les nombres avec une virgule décimale (0,84) ; recopie "
    "le tx_id, le score, la confiance, le schéma, chaque facteur avec son poids "
    "et chaque transaction voisine ; cite les textes réglementaires pertinents "
    "(GAFI, droit marocain) ; n'invente aucune valeur."
)


# --- 0. Utilitaires ----------------------------------------------------------

def load_jsonl(path) -> list:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def set_seed(seed: int) -> None:
    random.seed(seed)
    try:
        import numpy as np
        np.random.seed(seed)
    except ImportError:
        pass
    try:
        import torch
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
    except ImportError:
        pass


def _sync() -> None:
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.synchronize()
    except ImportError:
        pass


# --- 1. Prompts -------------------------------------------------------------

def user_message(alert_json: str, instruction: str, context: str = None) -> str:
    text = f"{instruction}\n\nAlerte :\n{alert_json}"
    if context:
        text += (
            "\n\nExtraits de textes réglementaires (cite-les si pertinent, "
            "sans en inventer d'autres) :\n" + context
        )
    return text


def prompt_text(tokenizer, alert_json: str, instruction: str = INSTRUCTION,
                context: str = None) -> str:
    """Texte complet du prompt (gabarit de chat du modèle + amorce de réponse).

    On passe par tokenize=False puis on tokenise nous-mêmes : le type de retour
    de apply_chat_template(tokenize=True) a changé selon les versions de
    transformers, pas le texte.
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message(alert_json, instruction, context)},
    ]
    return tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )


# --- 2. Encodage et masquage ------------------------------------------------

def encode_example(tokenizer, record: dict) -> dict:
    """Tokenise un exemple. labels = -100 sur le prompt, ids du rapport ensuite.

    La perte (loss) ne porte donc QUE sur le rapport : le modèle apprend à
    écrire le rapport, pas à recopier l'instruction ni l'alerte. Le jeton de fin
    (eos) est inclus dans la cible pour qu'il apprenne aussi à s'arrêter.
    """
    prompt = prompt_text(tokenizer, record["input"], record["instruction"])
    answer = record["output"] + tokenizer.eos_token
    p_ids = tokenizer(prompt, add_special_tokens=False)["input_ids"]
    a_ids = tokenizer(answer, add_special_tokens=False)["input_ids"]
    return {"input_ids": p_ids + a_ids, "labels": [-100] * len(p_ids) + a_ids}


def build_dataset(tokenizer, records: list) -> list:
    return [encode_example(tokenizer, r) for r in records]


def token_stats(dataset: list) -> dict:
    lens = [len(e["input_ids"]) for e in dataset]
    ans = [sum(1 for t in e["labels"] if t != -100) for e in dataset]
    return {
        "n": len(dataset),
        "total_tokens_mean": sum(lens) / len(lens),
        "total_tokens_max": max(lens),
        "report_tokens_mean": sum(ans) / len(ans),
        "report_tokens_max": max(ans),
    }


def collate(batch: list, pad_id: int) -> dict:
    """Complète les séquences à droite (padding) pour former un lot."""
    import torch

    n = max(len(b["input_ids"]) for b in batch)
    ids = torch.full((len(batch), n), pad_id, dtype=torch.long)
    labels = torch.full((len(batch), n), -100, dtype=torch.long)
    mask = torch.zeros((len(batch), n), dtype=torch.long)
    for i, b in enumerate(batch):
        length = len(b["input_ids"])
        ids[i, :length] = torch.tensor(b["input_ids"])
        labels[i, :length] = torch.tensor(b["labels"])
        mask[i, :length] = 1
    return {"input_ids": ids, "attention_mask": mask, "labels": labels}


# --- 3. LoRA ----------------------------------------------------------------

# Toutes les projections linéaires de l'attention et du MLP (usage standard
# pour les modèles Qwen / Llama).
LORA_TARGETS = ["q_proj", "k_proj", "v_proj", "o_proj",
                "gate_proj", "up_proj", "down_proj"]


def count_params(model) -> tuple:
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    return trainable, total


def apply_lora(base_model, rank: int, alpha: int = None, dropout: float = 0.05,
               targets: list = None):
    """Ajoute des adaptateurs LoRA de rang `rank` au modèle de base.

    alpha = 2 x rang par défaut : le facteur d'échelle alpha/rang reste égal à 2
    quel que soit le rang, ce qui isole l'effet de la CAPACITÉ (rang) de celui
    de l'amplitude de la mise à jour.
    """
    from peft import LoraConfig, get_peft_model

    config = LoraConfig(
        r=rank,
        lora_alpha=alpha if alpha else 2 * rank,
        lora_dropout=dropout,
        target_modules=targets or LORA_TARGETS,
        bias="none",
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(base_model, config)
    # Les adaptateurs restent en float32 même si le modèle de base est en
    # float16 : l'entraînement en précision mixte (GradScaler) l'exige.
    for p in model.parameters():
        if p.requires_grad:
            p.data = p.data.float()
    return model


def _label_tokens(example: dict) -> int:
    return sum(1 for t in example["labels"] if t != -100)


def validation_loss(model, data: list, pad_id: int, batch_size: int,
                    device: str, use_amp: bool) -> float:
    """Perte moyenne par jeton du rapport, sur un jeu de validation."""
    import torch

    model.eval()
    total, count = 0.0, 0
    with torch.no_grad():
        for s in range(0, len(data), batch_size):
            chunk = data[s:s + batch_size]
            batch = {k: v.to(device) for k, v in collate(chunk, pad_id).items()}
            with torch.autocast(device_type="cuda", dtype=torch.float16,
                                enabled=use_amp):
                loss = model(**batch).loss
            n = sum(_label_tokens(e) for e in chunk)
            total += loss.item() * n
            count += n
    model.train()
    return total / count


def train_lora(base_model, tokenizer, train_data: list, val_data: list, rank: int,
               *, epochs: int = 2, lr: float = 2e-4, batch_size: int = 4,
               grad_accum: int = 4, seed: int = 42, device: str = "cuda",
               use_amp: bool = True, log_every: int = 5, alpha: int = None,
               dropout: float = 0.05, verbose: bool = True) -> dict:
    """Entraîne un LoRA de rang `rank` sur un modèle de base FRAIS.

    `base_model` est modifié en place (get_peft_model) : recharge-le pour chaque
    rang. Retourne le modèle LoRA et les mesures demandées par le cahier :
    paramètres entraînables, temps d'entraînement, courbes de perte.
    """
    import torch

    set_seed(seed)
    pad_id = tokenizer.pad_token_id
    model = apply_lora(base_model, rank, alpha, dropout).to(device)
    model.config.use_cache = False
    trainable, total = count_params(model)
    if verbose:
        print(f"rang {rank} : {trainable:,} paramètres entraînables sur "
              f"{total:,} ({100 * trainable / total:.2f} %)")

    params = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.AdamW(params, lr=lr, weight_decay=0.0)
    group = batch_size * grad_accum
    total_steps = epochs * math.ceil(len(train_data) / group)
    warmup = max(1, int(0.05 * total_steps))

    def lr_factor(step):  # montée linéaire puis descente linéaire
        if step < warmup:
            return (step + 1) / warmup
        return max(0.0, (total_steps - step) / max(1, total_steps - warmup))

    scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lr_factor)
    scaler = torch.amp.GradScaler("cuda", enabled=use_amp)

    rng = random.Random(seed)
    history, val_losses = [], []
    step, run_loss, run_tokens = 0, 0.0, 0
    if device == "cuda":
        torch.cuda.reset_peak_memory_stats()
    _sync()
    t0 = time.time()
    model.train()

    for epoch in range(epochs):
        order = list(range(len(train_data)))
        rng.shuffle(order)
        for g in range(0, len(order), group):
            chunk = order[g:g + group]
            group_tokens = sum(_label_tokens(train_data[i]) for i in chunk)
            for m in range(0, len(chunk), batch_size):
                mb = chunk[m:m + batch_size]
                batch = collate([train_data[i] for i in mb], pad_id)
                batch = {k: v.to(device) for k, v in batch.items()}
                with torch.autocast(device_type="cuda", dtype=torch.float16,
                                    enabled=use_amp):
                    loss = model(**batch).loss
                if not torch.isfinite(loss):
                    raise RuntimeError(
                        "Perte NaN/inf : essaie use_amp=False (ou un modèle "
                        "chargé en float32), ou baisse le taux d'apprentissage."
                    )
                mb_tokens = sum(_label_tokens(train_data[i]) for i in mb)
                # pondération par les jetons : moyenne exacte sur le groupe
                scaler.scale(loss * (mb_tokens / group_tokens)).backward()
                run_loss += loss.item() * mb_tokens
                run_tokens += mb_tokens
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(params, 1.0)
            scaler.step(optimizer)
            scaler.update()
            optimizer.zero_grad(set_to_none=True)
            scheduler.step()
            step += 1
            if step % log_every == 0 or step == total_steps:
                history.append((step, run_loss / run_tokens))
                if verbose:
                    print(f"  étape {step}/{total_steps} | perte {run_loss / run_tokens:.4f}")
                run_loss, run_tokens = 0.0, 0
        if val_data:
            vl = validation_loss(model, val_data, pad_id, batch_size, device, use_amp)
            val_losses.append(vl)
            if verbose:
                print(f"  fin époque {epoch + 1}/{epochs} | perte validation {vl:.4f}")

    _sync()
    train_seconds = time.time() - t0
    model.eval()
    model.config.use_cache = True
    peak_gb = (torch.cuda.max_memory_allocated() / 1e9) if device == "cuda" else None
    return {
        "model": model,
        "rank": rank,
        "trainable_params": trainable,
        "total_params": total,
        "train_seconds": train_seconds,
        "history": history,
        "val_losses": val_losses,
        "peak_gpu_gb": peak_gb,
    }


# --- 4. Génération -----------------------------------------------------------

def generate_reports(model, tokenizer, prompts: list, *, max_new_tokens: int = 1000,
                     batch_size: int = 8, device: str = "cuda",
                     use_amp: bool = True) -> list:
    """Génère un rapport par prompt, par lots, de façon déterministe (greedy).

    repetition_penalty = 1.0 est FORCÉ : la configuration par défaut de Qwen
    applique 1,05, ce qui pénalise la recopie répétée d'un même identifiant ou
    d'un même nombre, justement ce que l'on veut mesurer.
    """
    import torch

    model.eval()
    old_side = tokenizer.padding_side
    tokenizer.padding_side = "left"  # indispensable pour générer par lots
    order = sorted(range(len(prompts)), key=lambda i: len(prompts[i]))
    outputs = [None] * len(prompts)
    for s in range(0, len(order), batch_size):
        idx = order[s:s + batch_size]
        enc = tokenizer([prompts[i] for i in idx], return_tensors="pt",
                        padding=True, add_special_tokens=False).to(device)
        with torch.inference_mode(), torch.autocast(
                device_type="cuda", dtype=torch.float16, enabled=use_amp):
            gen = model.generate(
                **enc,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                temperature=None, top_p=None, top_k=None,
                repetition_penalty=1.0,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
                use_cache=True,
            )
        new_tokens = gen[:, enc["input_ids"].shape[1]:]
        for i, text in zip(idx, tokenizer.batch_decode(new_tokens,
                                                       skip_special_tokens=True)):
            outputs[i] = text.strip()
    tokenizer.padding_side = old_side
    return outputs


# --- 5. RAG ------------------------------------------------------------------

STR_QUERY = ("Quand une institution financière doit-elle déclarer une opération "
             "suspecte à la cellule de renseignement financier ?")

# L'alerte ne contient pas de texte : la question posée à la base vectorielle
# dépend donc du schéma détecté. Conséquence à connaître : toutes les alertes
# d'un même schéma reçoivent le même contexte (4 recherches au total).
RAG_QUERIES = {
    "cycle": ("Obligations de vigilance et de déclaration de soupçon face à des "
              "transactions circulaires de blanchiment (empilement, layering)"),
    "fan-in": ("Obligations de vigilance et de déclaration de soupçon pour un "
               "compte qui reçoit des fonds de nombreux comptes (compte mule)"),
    "fan-out": ("Obligations de vigilance et informations sur les virements "
                "électroniques pour un compte qui disperse des fonds vers de "
                "nombreux comptes"),
    "none": ("Obligations de vigilance à l'égard de la clientèle et examen des "
             "transactions inhabituelles"),
}


def retrieve_context(alert: dict, search_fn, k: int = 2, max_words: int = 180) -> str:
    """Contexte réglementaire : k extraits (source + pages), tronqués à max_words.

    On alterne entre la question propre au schéma et la question sur la
    déclaration de soupçon, pour être sûr d'avoir cette dernière.
    """
    queries = [RAG_QUERIES[alert["pattern"]], STR_QUERY]
    results = [search_fn(q, k) for q in queries]
    seen, parts = set(), []
    for rank in range(k):
        for hits in results:
            if rank >= len(hits) or len(parts) >= k:
                continue
            hit = hits[rank]
            key = (hit["source"], hit["pages"])
            if key in seen:
                continue
            seen.add(key)
            words = hit["text"].split()
            text = " ".join(words[:max_words]) + (" […]" if len(words) > max_words else "")
            parts.append(f'[{len(parts) + 1}] {hit["source"]}, p.{hit["pages"]} : {text}')
    return "\n".join(parts)


def build_contexts(alerts: list, search_fn, k: int = 2, max_words: int = 180) -> dict:
    """{tx_id: contexte}, avec une seule recherche par schéma (mise en cache)."""
    cache, contexts = {}, {}
    for a in alerts:
        if a["pattern"] not in cache:
            cache[a["pattern"]] = retrieve_context(a, search_fn, k, max_words)
        contexts[a["tx_id"]] = cache[a["pattern"]]
    return contexts


# --- 6. Métriques -------------------------------------------------------------

_REF_ANY = re.compile(r"\b(GAFI|FATF|RGPD|loi)\b|Recommandation\s+\d+|droit marocain",
                      re.IGNORECASE)
_REF_R20 = re.compile(r"Recommandation\s*(n°\s*)?20\b|\bR\.?\s?20\b", re.IGNORECASE)


def score_report(alert: dict, report: str) -> dict:
    """Mesures automatiques d'un rapport.

    facts_ok     : tous les faits de l'alerte repris, rien d'inventé (report_checks)
    n_problems   : nombre d'écarts (0 = parfait)
    sections_ok  : les 5 sections présentes, dans l'ordre (proxy de CLARTÉ de structure)
    cite_any     : cite au moins un texte réglementaire (GAFI, loi, RGPD...)
    cite_R20     : cite la recommandation 20 (déclaration des opérations suspectes)
    La lisibilité réelle et la justesse des citations se jugent à la main sur
    un échantillon (relecture manuelle exigée par le cahier).
    """
    ok, problems = check_report(alert, report)
    positions = [report.find(s) for s in SECTIONS]
    return {
        "facts_ok": ok,
        "n_problems": len(problems),
        "problems": problems,
        "sections_ok": all(p >= 0 for p in positions) and positions == sorted(positions),
        "cite_any": bool(_REF_ANY.search(report)),
        "cite_R20": bool(_REF_R20.search(report)),
        "n_words": len(report.split()),
    }


def summarize(scores: list) -> dict:
    n = len(scores)

    def pct(key):
        return round(100 * sum(1 for s in scores if s[key]) / n, 1)

    return {
        "n": n,
        "facts_ok_%": pct("facts_ok"),
        "mean_problems": round(sum(s["n_problems"] for s in scores) / n, 2),
        "sections_ok_%": pct("sections_ok"),
        "cite_any_%": pct("cite_any"),
        "cite_R20_%": pct("cite_R20"),
        "avg_words": round(sum(s["n_words"] for s in scores) / n),
    }


def evaluate_model(model, tokenizer, records: list, *, instruction: str = None,
                   contexts: dict = None, max_new_tokens: int = 1000,
                   batch_size: int = 8, device: str = "cuda",
                   use_amp: bool = True) -> dict:
    """Génère les rapports du jeu de test et les note automatiquement.

    instruction=None : on utilise l'instruction stockée dans chaque exemple
                       (celle du LoRA). contexts : {tx_id: texte RAG} ou None.
    """
    alerts = [json.loads(r["input"]) for r in records]
    prompts = [
        prompt_text(tokenizer, r["input"], instruction or r["instruction"],
                    contexts[a["tx_id"]] if contexts else None)
        for r, a in zip(records, alerts)
    ]
    _sync()
    t0 = time.time()
    reports = generate_reports(model, tokenizer, prompts,
                               max_new_tokens=max_new_tokens,
                               batch_size=batch_size, device=device,
                               use_amp=use_amp)
    _sync()
    gen_seconds = time.time() - t0
    scores = [score_report(a, rep) for a, rep in zip(alerts, reports)]
    return {"reports": reports, "scores": scores, "summary": summarize(scores),
            "gen_seconds": gen_seconds}


def write_samples_markdown(path, results_by_config: dict, records: list,
                           n: int = 3) -> None:
    """Écrit n exemples par configuration pour la relecture manuelle."""
    lines = ["# Échantillon pour relecture manuelle (B4)", ""]
    for config, res in results_by_config.items():
        lines += [f"## {config}", ""]
        for i in range(min(n, len(records))):
            lines += [
                f"### Exemple {i + 1} — {records[i]['id']}",
                "Entrée : `" + records[i]["input"] + "`",
                f"Contrôle automatique : {res['scores'][i]['problems'] or 'aucun écart'}",
                "", "```", res["reports"][i], "```", "",
                "Grille : clarté __/5 | citations justes __/5 | remarques :", "",
            ]
    Path(path).write_text("\n".join(lines), encoding="utf-8")
