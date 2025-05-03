from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from app.db.models.document import Document
from app.schemas.document import DocumentOut
from app.api.deps import get_db, get_current_user
from typing import List
from app.utils.file_utils import extract_text_from_pdf

import uuid

router = APIRouter()


@router.post("/", response_model=DocumentOut)
def upload_document(
    title: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # save the file to a temporary location
    file_location = f"files/{file.filename}"
    with open(file_location, "wb") as file_object:
        file_object.write(file.file.read())
    file.file.seek(0)  # Reset file pointer to the beginning

    content = extract_text_from_pdf(file.file)
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not extract text from the provided PDF file.",
        )
    new_doc = Document(
        id=str(uuid.uuid4()),
        title=title,
        file_name=file.filename,
        file_type=file.content_type,
        file_size=file.size,
        content=content,
        owner_id=current_user.id,
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    return new_doc


@router.get("/", response_model=List[DocumentOut])
def list_documents(
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    return db.query(Document).filter(Document.owner_id == current_user.id).all()
