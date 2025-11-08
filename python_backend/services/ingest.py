"""Document ingestion with OCR and topic extraction"""
from typing import List
from sqlmodel import Session
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import os


async def process_document(
    file_path: str,
    user_id: str,
    session: Session,
) -> List[any]:
    """Process uploaded document and extract topics"""
    from ..models import Topic, Document
    from ..rag import RAGSystem
    
    # Extract text based on file type
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext == ".pdf":
        # PDF processing with OCR
        images = convert_from_path(file_path)
        extracted_text = ""
        for img in images:
            text = pytesseract.image_to_string(img)
            extracted_text += text + "\n\n"
    
    elif file_ext in [".png", ".jpg", ".jpeg"]:
        # Image OCR
        img = Image.open(file_path)
        extracted_text = pytesseract.image_to_string(img)
    
    elif file_ext == ".txt":
        # Plain text
        with open(file_path, "r", encoding="utf-8") as f:
            extracted_text = f.read()
    
    else:
        extracted_text = "Unsupported file format"
    
    # Add to RAG system
    rag = RAGSystem(user_id)
    vector_ids = await rag.add_documents(
        texts=[extracted_text],
        source=os.path.basename(file_path),
    )
    
    # Save document record
    document = Document(
        userId=user_id,
        filename=os.path.basename(file_path),
        contentType=file_ext,
        extractedText=extracted_text[:5000],  # Store first 5000 chars
        vectorIds=vector_ids,
    )
    session.add(document)
    session.commit()
    
    # Extract topics using simple keyword extraction
    # In production, would use NLP/LLM for better topic extraction
    topics_data = extract_topics_from_text(extracted_text)
    
    topics = []
    for topic_data in topics_data:
        topic = Topic(
            userId=user_id,
            name=topic_data["name"],
            importanceScore=topic_data["importance"],
            masteryScore=topic_data["mastery"],
        )
        session.add(topic)
        topics.append(topic)
    
    session.commit()
    return topics


def extract_topics_from_text(text: str) -> List[dict]:
    """Extract topics from text (simplified)"""
    # Mock topic extraction
    # In production: use NLP libraries or LLM for better extraction
    
    keywords = ["database", "sql", "algorithm", "data structure", "network", "security"]
    found_topics = []
    
    text_lower = text.lower()
    for keyword in keywords:
        if keyword in text_lower:
            found_topics.append({
                "name": keyword.title(),
                "importance": 8,  # Would be calculated based on frequency, context
                "mastery": 50,  # Default starting mastery
            })
    
    # If no keywords found, add default topics
    if not found_topics:
        found_topics = [
            {"name": "General Concepts", "importance": 7, "mastery": 50},
            {"name": "Core Principles", "importance": 8, "mastery": 50},
        ]
    
    return found_topics[:10]  # Limit to 10 topics
