from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from app.db.models.document import Document
from app.schemas.document import DocumentOut
from app.api.deps import get_db, get_current_user
from llama_index.core.schema import Document as LlamaDocument

from app.db.postgres import get_vector_store
from app.utils.file_utils import extract_text_from_pdf

from typing import List

from app.services.embedder import Embedder

import uuid
import os

router = APIRouter()


@router.post("/", response_model=DocumentOut)
def upload_document(
    title: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    vector_store=Depends(get_vector_store),
):
    allowed_types = ["application/pdf", "text/plain"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PDF and TXT files are allowed.",
        )

    if not os.path.exists("files"):
        os.makedirs("files")

    file_ext = file.filename.split(".")[-1].lower()
    file_location = f"files/{file.filename}"

    # Save the file to disk
    with open(file_location, "wb") as file_object:
        file_object.write(file.file.read())
    file.file.seek(0)

    if file.content_type == "application/pdf" or file_ext == "pdf":
        content = extract_text_from_pdf(file_location)

    elif file.content_type == "text/plain" or file_ext == "txt":
        content = file.file.read().decode("utf-8")
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format.",
        )

    content = content.replace("\x00", "") if content else ""
    if not content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No readable content found in the uploaded file.",
        )

    # Save document to DB
    new_doc = Document(
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

    print(new_doc.id)

    # Embedding
    embedder = Embedder()

    # Use a text loader fallback for txt files
    if file_ext == "txt":
        docs = [LlamaDocument(**{"text": content, "metadata": {}})]
    else:
        docs = embedder.load_documents(file_location)

    shared_metadata = {
        "document_id": new_doc.id,
        "file_name": file.filename,
        "file_type": file.content_type,
        "file_size": file.size,
        "title": title,
        "owner_id": current_user.id,
        "source": file_location,
    }

    text_chunks, doc_idxs = embedder.text_splitter(docs)
    nodes = embedder.create_text_nodes(text_chunks, docs, doc_idxs, shared_metadata)
    nodes = embedder.embed_text_nodes(nodes)

    # for node in nodes:
    #     node.metadata.update(
    #         {
    #             "document_id": new_doc.id,
    #             "file_name": file.filename,
    #             "file_type": file.content_type,
    #             "file_size": file.size,
    #             "title": title,
    #             "owner_id": current_user.id,
    #             "source": file_location,
    #         }
    #     )
    print(f"Nodes metadata: {nodes[0].metadata}")

    vector_store.add(nodes)

    return new_doc


@router.get("/", response_model=List[DocumentOut])
def list_documents(
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    return db.query(Document).filter(Document.owner_id == current_user.id).all()
