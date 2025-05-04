from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from app.db.models.document import Document
from app.schemas.document import DocumentOut
from app.api.deps import get_db, get_current_user

from app.db.postgres import get_vector_store
from app.utils.file_utils import extract_text_from_pdf

from typing import List

from app.services.embedder import Embedder

import uuid

router = APIRouter()


@router.post("/", response_model=DocumentOut)
def upload_document(
    title: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    vector_store=Depends(get_vector_store),
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed.",
        )
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PDF files are allowed.",
        )

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

    # Create embedding
    embedder = Embedder()

    docs = embedder.load_documents(file_location)
    print("DOCUMENTS", docs)

    text_chunks, doc_idxs = embedder.text_splitter(docs)
    nodes = embedder.create_text_nodes(text_chunks, docs, doc_idxs)
    nodes = embedder.embed_text_nodes(nodes)
    for node in nodes:
        node.metadata["doc_id"] = new_doc.id
        node.metadata["file_name"] = file.filename
        node.metadata["file_type"] = file.content_type
        node.metadata["file_size"] = file.size
        node.metadata["title"] = title
        node.metadata["owner_id"] = current_user.id
        node.metadata["source"] = file_location

    print(nodes)

    vector_store.add(nodes)
    return new_doc


@router.get("/", response_model=List[DocumentOut])
def list_documents(
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    return db.query(Document).filter(Document.owner_id == current_user.id).all()
