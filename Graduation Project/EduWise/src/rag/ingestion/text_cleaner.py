# Clean extracted text
# الهدف:
# - إزالة المسافات الزائدة.
# - تحسين تنسيق النص.
# - تجاهل الصفحات التي تحتوي على نص قليل جدًا.
# - التأكد من وجود كمية كافية من النص لمعالجة المستند.


# min_page_chars: أقل عدد أحرف لقبول الصفحة.
# min_total_chars: أقل عدد أحرف مطلوب للمستند بالكامل.
def clean_pages(raw_pages: list[str], min_page_chars: int = 50, min_total_chars: int = 200) -> str:
    cleaned_pages: list[str] = []
    for page_text in raw_pages:
        normalized = " ".join(page_text.split())
        normalized = normalized.replace(" .", ".").replace(" ,", ",")
        if len(normalized.strip()) > min_page_chars:
            cleaned_pages.append(normalized.strip())

    full_text = "\n\n".join(cleaned_pages) # يجمع الصفحات في نص واحد مع ترك سطرين بين كل صفحة
    if len(full_text.strip()) < min_total_chars:
        raise ValueError(
            "Insufficient selectable text extracted from PDF. "
            "Ensure the PDF contains typed text rather than scanned images only."
        )
    return full_text