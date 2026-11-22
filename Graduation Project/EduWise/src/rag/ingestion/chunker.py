# Split text into chunks
# مسؤول عن تقسيم النص المستخرج والمنظّف إلى أجزاء صغيرة (Chunks) قبل تحويلها إلى Embeddings وتخزينها في FAISS.
# الهدف هو تجهيز النصوص بحيث يستطيع نظام RAG استرجاع الأجزاء الأكثر ارتباطًا بالسؤال.
from langchain_text_splitters import RecursiveCharacterTextSplitter
# استخدام Recursive Character Splitter لتقسيم النص مع محاولة الحفاظ على ترابط الجمل والفقرات.

def split_text_into_chunks(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
    min_chunk_chars: int = 80,
) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""],
    )
    chunks = splitter.split_text(text)
    return [c for c in chunks if len(c.strip()) > min_chunk_chars]