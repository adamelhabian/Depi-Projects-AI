# Connect the complete RAG workflow


import json
import time
from pathlib import Path
from typing import Any

from config.settings import RAGSettings, settings
from rag.embeddings.embedder import TextEmbedder
from rag.evaluation.generation_metrics import measure_complexity
from rag.evaluation.retrieval_metrics import evaluate_retrieval_context
from rag.export.pdf_generator import format_exam_paper, generate_pdf_exam
from rag.generation.exam_generator import ExamGenerator
from rag.generation.llm_client import GroqLLMClient
from rag.ingestion.chunker import split_text_into_chunks
from rag.ingestion.pdf_loader import load_pdf_pages
from rag.ingestion.text_cleaner import clean_pages
from rag.retrieval.semantic_retriever import SemanticRetriever
from rag.vector_store.faiss_store import FaissVectorStore


def run_exam_pipeline(
    pdf_path: str | Path,
    subject: str = "Study Material",
    difficulty: str | None = None,
    question_types: list[str] | None = None,
    questions_per_type: int | None = None,
    cfg: RAGSettings = settings,
    rate_limit_sleep: float = 1.0,
) -> dict[str, Any]:

    # Validate configuration
    cfg.validate()

    active_difficulty = (
        difficulty if difficulty is not None else cfg.default_difficulty
    )
    active_types = (
        question_types if question_types is not None else cfg.question_types
    )
    active_count = (
        questions_per_type
        if questions_per_type is not None
        else cfg.questions_per_type
    )

    if not active_types:
        raise ValueError("At least one question type is required.")

    if active_count <= 0:
        raise ValueError("Questions per type must be positive.")

    # 1. Ingestion & Chunking
    raw_pages = load_pdf_pages(pdf_path)
    cleaned_text = clean_pages(raw_pages)

    chunks = split_text_into_chunks(
        cleaned_text,
        chunk_size=cfg.chunk_size,
        chunk_overlap=cfg.chunk_overlap,
    )

    if not chunks:
        raise ValueError("No text chunks were extracted from the PDF.")

    # 2. Embeddings & FAISS Vector Store
    embedder = TextEmbedder(model_name=cfg.embedding_model)

    chunk_vectors = embedder.encode(chunks)

    vector_store = FaissVectorStore(
        dimension=chunk_vectors.shape[1]
    )
    vector_store.add(chunk_vectors, chunks)

    # 3. Semantic Retrieval
    semantic_retriever = SemanticRetriever(
        vector_store=vector_store,
        embedder=embedder,
    )

    # 4. LLM Client & Question Generator
    llm_client = GroqLLMClient()

    generator = ExamGenerator(
        llm_client=llm_client,
        marks_per_type=cfg.marks_per_type,
    )

    rag_results: dict[str, list[dict]] = {}
    retrieval_metrics: dict[str, dict[str, Any]] = {}

    for index, q_type in enumerate(active_types):

        query = (
            f"{active_difficulty} level {q_type} questions covering "
            "main concepts, definitions, and key topics"
        )

        # Retrieve relevant context using semantic search
        rag_context = semantic_retriever.retrieve(
            query=query,
            top_k=cfg.top_k_chunks,
        )

        # Evaluate retrieval performance
        retrieval_metrics[q_type] = evaluate_retrieval_context(
            query=query,
            vector_store=vector_store,
            embedder=embedder,
            top_k=cfg.top_k_chunks,
        )

        # Generate questions
        rag_results[q_type] = generator.generate_for_type(
            context=rag_context,
            q_type=q_type,
            difficulty=active_difficulty,
            count=active_count,
        )["questions"]

        if rate_limit_sleep > 0 and index < len(active_types) - 1:
            time.sleep(rate_limit_sleep)

    # 5. Evaluation
    metrics = {
        "retrieval": retrieval_metrics,
        "generation_complexity": measure_complexity(
            {"sections": rag_results}
        ),
    }

    # 6. Export TXT, JSON & PDF
    out_dir = Path(cfg.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    diff_slug = active_difficulty.lower().replace(" ", "_")

    rag_text = format_exam_paper(
        sections=rag_results,
        difficulty=active_difficulty,
        subject=subject,
        source_file=str(pdf_path),
        marks_per_type=cfg.marks_per_type,
        model_name=cfg.groq_model,
    )

    rag_txt_path = out_dir / f"exam_paper_RAG_{diff_slug}.txt"
    json_path = out_dir / "raw_results.json"
    rag_pdf_path = out_dir / f"exam_paper_RAG_{diff_slug}.pdf"

    # Save TXT
    rag_txt_path.write_text(
        rag_text,
        encoding="utf-8",
    )

    # Save JSON
    json_path.write_text(
        json.dumps(
            {
                "subject": subject,
                "source_file": str(pdf_path),
                "difficulty": active_difficulty,
                "results": rag_results,
                "metrics": metrics,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    # Generate PDF
    generate_pdf_exam(
        sections=rag_results,
        difficulty=active_difficulty,
        subject=subject,
        source_file=str(pdf_path),
        output_path=str(rag_pdf_path),
        marks_per_type=cfg.marks_per_type,
    )

    return {
        "chunks_count": len(chunks),
        "rag_results": rag_results,
        "metrics": metrics,
        "files": {
            "rag_txt": str(rag_txt_path),
            "raw_json": str(json_path),
            "rag_pdf": str(rag_pdf_path),
        },
    }