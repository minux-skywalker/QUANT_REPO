from fastapi import FastAPI, UploadFile, File
from typing import List
import pandas as pd
from app.scorer import score_resume
from app.parser import extract_text_from_file
from fastapi.middleware.cors import CORSMiddleware



app=FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 👈 You can restrict this later to ["http://localhost:3000"] etc.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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