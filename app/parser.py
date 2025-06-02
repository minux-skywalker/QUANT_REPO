import os
import uuid
from fastapi import UploadFile
import aiofiles
from docx import Document
import fitz  # for PDFs

async def extract_text_from_file(file: UploadFile) -> str:
    filename = file.filename.lower()
    
    # Make a unique temp path
    extension = os.path.splitext(filename)[1]
    temp_path = f"temp_{uuid.uuid4().hex}{extension}"

    # Save temp file
    async with aiofiles.open(temp_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
    
    # Detect format
    if filename.endswith(".docx"):
        text = extract_docx(temp_path)
    elif filename.endswith(".txt"):
        text = extract_txt(temp_path)
    elif filename.endswith(".pdf"):
        text = extract_pdf(temp_path)
    else:
        text = "Unsupported file type"
    
    os.remove(temp_path)
    return text

def extract_docx(path: str) -> str:
    doc = Document(path)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_txt(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def extract_pdf(path: str) -> str:
    text = ""
    with fitz.open(path) as doc:
        for page in doc:
            text += page.get_text()
    return text
