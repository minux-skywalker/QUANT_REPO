import os
from docx import Document
from fastapi import UploadFile
import aiofiles

async def extract_text_from_file(file:UploadFile)-> str:
    filename = file.filename.lower()
    
    #Save Temporarily
    temp_path=f"temp_{filename}"
    async with aiofiles.open(temp_path, 'wb') as out_file:
        content=await file.read()
        await out_file.write(content)
        
    if filename.endswith(".docx"):
        text=extract_docx(temp_path)
    elif filename.endswith(".txt"):
        text=extract_txt(temp_path)
    else:
        text = "Unsupported file type"  # Later we’ll add .pdf support
    
    os.remove(temp_path)
    return text

def extract_docx(path:str)->str:
    doc=Document(path)
    return "\n".join([para.text for para in doc.paragraphs])
        
def extract_txt(path:str)->str:
    with open(path,'r',encoding='utf-8') as f:
        return f.read()
    