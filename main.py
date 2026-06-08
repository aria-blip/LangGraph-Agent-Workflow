from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import shutil
import os
from ai_service import ask_ai

app = FastAPI(title="Supply Chain Analyzer API")

# Ordner erstellen, falls sie nicht existieren
os.makedirs("storage", exist_ok=True)
os.makedirs("frontend", exist_ok=True) # NEU: Hier kommt gleich unser HTML rein!

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dateien ausliefern
app.mount("/download", StaticFiles(directory="storage"), name="storage")

app.mount("/app", StaticFiles(directory="frontend", html=True), name="frontend")

@app.get("/")
def read_root():
    # Wenn man auf die Hauptseite geht, direkt zum Frontend weiterleiten
    return FileResponse("frontend/index.html")

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    file_path = f"storage/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"message": "Upload erfolgreich", "filename": file.filename}

@app.get("/ask")
def chat_with_ai(frage: str):
    antwort = ask_ai(frage)
    return {"ki_antwort": antwort}

def chat_with_ai(frage: str, thread_id: str = "default"):  
    antwort = ask_ai(frage, thread_id=thread_id)  # weiter leiten           
    return {"ki_antwort": antwort}

