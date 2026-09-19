"""Reproducible Lab 7 retrieval benchmark for the PTIT corpus."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from src import Document, EmbeddingStore, FixedSizeChunker, RecursiveChunker, SentenceChunker, _mock_embed

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

CORPUS_DIR = Path("data/quy-dinh-dai-hoc")
BENCHMARKS = [
    ("Hạn cuối để đăng ký nguyện vọng học lại cải thiện điểm là khi nào?", "hoc-lai", "25/09"),
    ("Nguyên tắc ưu tiên khi mở các lớp học lại là gì?", "hoc-lai", "5 sinh viên"),
    ("Ngành CNKT Điện, điện tử được chia thành những chuyên ngành nào?", "tuvan-khoa24", "Kỹ thuật điện tử máy tính"),
    ("Khi đăng ký học lại trên qldt, SV nhập gì vào ô Môn học?", "hoc-lai", "Mã môn"),
    ("Buổi tư vấn chọn chuyên ngành diễn ra ở phòng nào và lúc mấy giờ?", "tuvan-khoa24", "phòng 101 nhà A2"),
]


class HeadingChunker:
    """Split Markdown headings first; recursively split oversized sections."""

    def __init__(self, chunk_size: int = 500) -> None:
        self.chunk_size = chunk_size
        self.fallback = RecursiveChunker(chunk_size=chunk_size)

    def chunk(self, text: str) -> list[str]:
        sections = re.split(r"(?=^#{1,6}\s+)", text, flags=re.M)
        chunks: list[str] = []
        for section in sections:
            section = section.strip()
            if not section:
                continue
            title_match = re.match(r"^(#{1,6}\s+.+)$", section, flags=re.M)
            title = title_match.group(1) if title_match else ""
            parts = self.fallback.chunk(section)
            chunks.extend(part if not title or part.startswith(title) else f"{title}\n{part}" for part in parts)
        return chunks


def parse_document(path: Path) -> tuple[dict[str, str], str]:
    raw = path.read_text(encoding="utf-8")
    _, front_matter, content = raw.split("---", 2)
    metadata = {
        key: value.strip().strip('"')
        for key, value in re.findall(r"^(\w+):\s*(.+)$", front_matter, re.M)
    }
    return metadata, content.strip()


def make_chunker(name: str):
    return {
        "fixed": FixedSizeChunker(chunk_size=500, overlap=50),
        "sentence": SentenceChunker(max_sentences_per_chunk=3),
        "recursive": RecursiveChunker(chunk_size=500),
        "heading": HeadingChunker(chunk_size=500),
    }[name]


def ingest(chunker_name: str) -> EmbeddingStore:
    chunker = make_chunker(chunker_name)
    documents: list[Document] = []
    for path in sorted(CORPUS_DIR.glob("*.md")):
        metadata, content = parse_document(path)
        for index, chunk in enumerate(chunker.chunk(content)):
            documents.append(Document(f"{path.stem}#{index}", chunk, {**metadata, "doc_id": path.stem}))
    store = EmbeddingStore("ptit_benchmark", embedding_fn=_mock_embed)
    store.add_documents(documents)
    print(f"strategy={chunker_name}; chunks_loaded={store.get_collection_size()}; embedder=mock")
    return store


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strategy", choices=("fixed", "sentence", "recursive", "heading"), default="sentence")
    args = parser.parse_args()
    store = ingest(args.strategy)
    for number, (query, gold_doc, gold_text) in enumerate(BENCHMARKS, start=1):
        metadata_filter = {"audience": "student"} if number == 5 else None
        results = store.search_with_filter(query, top_k=3, metadata_filter=metadata_filter)
        print(f"\nQ{number}: {query}")
        for rank, result in enumerate(results, start=1):
            contains_gold = gold_text.lower() in result["content"].lower()
            print(f"  {rank}. score={result['score']:.4f} doc_id={result['metadata']['doc_id']} gold_text={contains_gold}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
