#!/usr/bin/env python3
"""B1 - Recherche dans la base vectorielle FAISS.

Sert de test de la base (questions d'essai) et de brique réutilisable pour
l'outil « recherche réglementaire » de l'agent (B6) via la fonction search().

Usage :
    python audit/search_rag.py                       # questions d'essai
    python audit/search_rag.py "structuring seuil de déclaration" -k 3
"""
import argparse
import json
from pathlib import Path

INDEX_DIR = Path(__file__).parent / "rag_index"

TEST_QUESTIONS = [
    "Quelles obligations de vigilance envers la clientèle pour les banques ?",
    "When must a financial institution file a suspicious transaction report?",
    "Quelles sont les règles de conservation des données personnelles ?",
    "Que dit la loi marocaine sur la déclaration de soupçon ?",
]

_cache = {}


def _load(index_dir: Path):
    key = str(index_dir)
    if key not in _cache:
        import faiss
        from sentence_transformers import SentenceTransformer

        meta = json.loads((index_dir / "index_meta.json").read_text(encoding="utf-8"))
        index = faiss.read_index(str(index_dir / "index.faiss"))
        with open(index_dir / "chunks.jsonl", encoding="utf-8") as f:
            chunks = [json.loads(line) for line in f]
        _cache[key] = (SentenceTransformer(meta["model"]), index, chunks, meta)
    return _cache[key]


def search(query: str, k: int = 3, index_dir: Path = INDEX_DIR) -> list:
    """Retourne les k chunks les plus proches, avec source, pages et score."""
    import numpy as np

    model, index, chunks, meta = _load(index_dir)
    q = model.encode(
        [meta.get("query_prefix", "") + query], normalize_embeddings=True
    )
    scores, ids = index.search(np.asarray(q, dtype="float32"), k)
    results = []
    for score, i in zip(scores[0], ids[0]):
        if i < 0:
            continue
        c = chunks[i]
        results.append({
            "score": round(float(score), 3),
            "source": c["source"],
            "pages": f'{c["page_start"]}-{c["page_end"]}',
            "text": c["text"],
        })
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("query", nargs="?", help="question (sinon : questions d'essai)")
    parser.add_argument("-k", type=int, default=3)
    args = parser.parse_args()

    for q in ([args.query] if args.query else TEST_QUESTIONS):
        print(f"\n=== {q}")
        for r in search(q, args.k):
            print(f'[{r["score"]}] {r["source"]} p.{r["pages"]}')
            print(f'    {r["text"][:200]}...')


if __name__ == "__main__":
    main()