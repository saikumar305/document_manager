import fitz
from fastapi import HTTPException, status


def extract_text_from_pdf(file_path: str) -> str:
    try:
        doc = fitz.open(file_path)
        return "\n".join(page.get_text() for page in doc)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error extracting text from PDF: {str(e)}",
        )
    finally:
        doc.close()
