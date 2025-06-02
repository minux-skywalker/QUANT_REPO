from fastapi import FastAPI, UploadFile, File
from typing import List
import pandas as pd
from app.scorer import score_resume
from app.parser import extract_text_from_file

app=FastAPI()

@app.post("/upload")
async def upload_files(jd:UploadFile= File(...), resumes:List[UploadFile]=File(...)):
    jd_text=await extract_text_from_file(jd)
    
    results=[]
    
    for resume in resumes:
        resume_text=await extract_text_from_file(resume)
        score, reason=score_resume(jd_text,resume_text)
        results.append({
            "name": resume.filename,
            "score": score,
            "reason":reason
        })
        
    return results