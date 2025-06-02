from fastapi import FastAPI, UploadFile, File
from typing import List
from app.scorer import score_resume
from app.parser import extract_text_from_file
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()

# ✅ Mount static files under /static
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

# ✅ Serve index.html at root so `/` loads frontend
@app.get("/")
async def root():
    return FileResponse("static/index.html")

# ✅ Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Upload endpoint for JD and resumes
@app.post("/upload")
async def upload_files(
    jd: UploadFile = File(...), resumes: List[UploadFile] = File(...)
):
    jd_text = await extract_text_from_file(jd)

    results = []
    for resume in resumes:
        resume_text = await extract_text_from_file(resume)
        score, reason = score_resume(jd_text, resume_text)
        results.append({"name": resume.filename, "score": score, "reason": reason})

    return results
