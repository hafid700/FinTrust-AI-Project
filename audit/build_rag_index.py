#!/usr/bin/env python3
"""B1 - Construction de la base vectorielle FAISS (RAG) pour FinTrust-AI.

Pipeline : PDF/TXT -> texte par page -> chunks (mots, avec chevauchement)
           -> embeddings -> index FAISS (+ métadonnées pour citer les sources).

Usage :
    python audit/build_rag_index.py
    python audit/build_rag_index.py --corpus audit/corpus --out audit/rag_index \
        --chunk-words 400 --overlap 80

Le dossier --corpus contient les documents publics (PDF ou .txt) : GAFI/FATF,
RGPD, textes marocains LAB/FT. Ce sont des documents CONSULTÉS par l'agent
(RAG), pas des données d'entraînement.
"""
import argparse
import json
import re
import unicodedata
from pathlib import Path

# Modèle multilingue : le corpus mélange anglais (GAFI/FATF) et français
# (RGPD, textes marocains). 384 dimensions, tourne sur CPU.
DEFAULT_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


# Certains PDF (ex. le guide LBC/FT marocain) encodent les ligatures « fi »,
# « ff », « fl » avec des idéogrammes : pypdf renvoie alors « dé昀椀ciences ».
# On les remplace avant tout (les plus longues d'abord).
LIGATURE_FIXES = [
    ("昀昀椀", "ffi"), ("昀昀氀", "ffl"), ("昀椀", "fi"), ("昀氀", "fl"), ("昀昀", "ff"),
]


def clean_text(text: str) -> str:
    """Nettoie le texte extrait d'un PDF (ligatures, césures, espaces)."""
    for bad, good in LIGATURE_FIXES:
        text = text.replace(bad, good)
    text = unicodedata.normalize("NFKC", text)  # ﬁ -> fi, espaces insécables...
    text = re.sub(r"-\n(?=\w)", "", text)  # mot coupé en fin de ligne
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def prefixes(model_name: str) -> tuple:
    """Les modèles E5 exigent les préfixes « query: » / « passage: »."""
    if "e5" in model_name.lower():
        return "query: ", "passage: "
    return "", ""


def read_pages(path: Path) -> list:
    """Retourne la liste des textes de pages (1 élément pour un .txt)."""
    if path.suffix.lower() == ".pdf":
        from pypdf import PdfReader  # import local : utile seulement ici

        reader = PdfReader(str(path))
        return [clean_text(page.extract_text() or "") for page in reader.pages]
    return [clean_text(path.read_text(encoding="utf-8", errors="ignore"))]


def chunk_pages(pages: list, size: int = 400, overlap: int = 80) -> list:
    """Découpe un document en chunks de `size` mots avec `overlap` mots communs.

    Chaque mot garde le numéro de sa page, pour que l'agent puisse citer
    « source, page X-Y » dans le rapport d'audit.
    Retourne une liste de dicts {text, page_start, page_end}.
    """
    if overlap >= size:
        raise ValueError("overlap doit être strictement inférieur à size")

    words = []  # (mot, numéro de page à partir de 1)
    for page_no, page_text in enumerate(pages, start=1):
        words.extend((w, page_no) for w in page_text.split())

    chunks, step = [], size - overlap
    for start in range(0, len(words), step):
        window = words[start:start + size]
        if len(window) < size // 4 and chunks:
            break  # morceau final trop court : déjà couvert par le chevauchement
        chunks.append({
            "text": " ".join(w for w, _ in window),
            "page_start": window[0][1],
            "page_end": window[-1][1],
        })
        if start + size >= len(words):
            break
    return chunks


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    here = Path(__file__).parent
    parser.add_argument("--corpus", type=Path, default=here / "corpus")
    parser.add_argument("--out", type=Path, default=here / "rag_index")
    parser.add_argument("--chunk-words", type=int, default=400)
    parser.add_argument("--overlap", type=int, default=80)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    args = parser.parse_args()

    files = sorted(
        p for p in args.corpus.glob("*") if p.suffix.lower() in {".pdf", ".txt"}
    )
    if not files:
        raise SystemExit(f"Aucun PDF/TXT trouvé dans {args.corpus}")

    records = []
    for path in files:
        pages = read_pages(path)
        chunks = chunk_pages(pages, args.chunk_words, args.overlap)
        for c in chunks:
            records.append({"id": len(records), "source": path.name, **c})
        print(f"{path.name}: {len(pages)} page(s) -> {len(chunks)} chunks")

    # Imports lourds ici pour que le découpage reste testable sans GPU/modèle.
    import faiss
    import numpy as np
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(args.model)
    query_prefix, passage_prefix = prefixes(args.model)
    embeddings = model.encode(
        [passage_prefix + r["text"] for r in records],
        batch_size=32,
        show_progress_bar=True,
        normalize_embeddings=True,  # produit scalaire == similarité cosinus
    )
    embeddings = np.asarray(embeddings, dtype="float32")

    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)

    args.out.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(args.out / "index.faiss"))
    with open(args.out / "chunks.jsonl", "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    (args.out / "index_meta.json").write_text(
        json.dumps({
            "model": args.model,
            "query_prefix": query_prefix,
            "dim": int(embeddings.shape[1]),
            "chunk_words": args.chunk_words,
            "overlap": args.overlap,
            "n_chunks": len(records),
        }, indent=2),
        encoding="utf-8",
    )
    print(f"Index de {len(records)} chunks écrit dans {args.out}")


if __name__ == "__main__":
    main()