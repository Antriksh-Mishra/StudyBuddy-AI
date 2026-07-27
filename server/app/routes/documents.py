import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.auth import User
from app.models.document import Document, DocumentChunk
from app.schemas.all_schemas import DocumentOut
from app.routes.auth import get_current_user
from app.services import ocr_service, ai_service, vector_db
from app.config import settings

router = APIRouter(prefix="/api/documents", tags=["Documents"])

@router.post("/upload", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Ensure upload directory exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # Save file locally
    file_path = os.path.join(settings.UPLOAD_DIR, f"{current_user.id}_{file.filename}")
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
        
    # Extract text based on file format
    file_ext = os.path.splitext(file.filename)[1].lower()
    extracted_text = ""
    
    if file_ext == ".pdf":
        extracted_text = ocr_service.extract_text_from_pdf(file_path)
    elif file_ext in [".png", ".jpg", ".jpeg"]:
        extracted_text = ocr_service.extract_text_from_image(file_path)
    else:
        # Cleanup file before raising error
        os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Please upload a PDF or an Image (PNG/JPG)."
        )
        
    # Create Document record in Database
    new_doc = Document(
        user_id=current_user.id,
        filename=file.filename,
        file_path=file_path,
        ocr_extracted_text=extracted_text,
        summary="Generating summary..."
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    
    # Generate RAG embeddings & chunks
    if extracted_text and extracted_text != "[Empty or unreadable document]":
        chunks = ai_service.chunk_text(extracted_text)
        
        vectors = []
        metadata_list = []
        
        for idx, chunk_text in enumerate(chunks):
            # Save chunk in PostgreSQL database
            new_chunk = DocumentChunk(
                document_id=new_doc.id,
                chunk_index=idx,
                text_content=chunk_text
            )
            db.add(new_chunk)
            
            # Generate embedding
            embedding = ai_service.get_embedding(chunk_text)
            vectors.append(embedding)
            
            # Metadata for FAISS lookup
            metadata_list.append({
                "document_id": new_doc.id,
                "chunk_index": idx,
                "text": chunk_text
            })
            
        db.commit()
        
        # Add to FAISS Vector Database
        if vectors:
            vector_db.add_vectors(vectors, metadata_list)
            
        # Generate summary using AI Service asynchronously or inline
        try:
            summary = ai_service.summarize_text(extracted_text)
            new_doc.summary = summary
            db.commit()
            db.refresh(new_doc)
        except Exception as e:
            print(f"[*] Summary generation failed: {e}")
            new_doc.summary = "Unable to generate summary. You can still ask questions about this document in the chat."
            db.commit()
            
    else:
        new_doc.summary = "Document contains no extractable text."
        db.commit()
        db.refresh(new_doc)
        
    return new_doc

@router.get("", response_model=List[DocumentOut])
def get_documents(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    docs = db.query(Document).filter(Document.user_id == current_user.id).order_by(Document.created_at.desc()).all()
    return docs

@router.get("/{document_id}", response_model=DocumentOut)
def get_document(document_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return doc

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        
    # Delete from local file system
    if os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except Exception as e:
            print(f"[*] Error deleting physical file {doc.file_path}: {e}")
            
    # Delete chunks from FAISS vector db
    vector_db.delete_document_vectors(doc.id)
    
    # Delete from PostgreSQL (cascade will delete DocumentChunk records)
    db.delete(doc)
    db.commit()
    return None
