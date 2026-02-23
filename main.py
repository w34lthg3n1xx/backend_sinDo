"""
FastAPI Entry Point - Legal Assistant Prototype
Stateless, Anonymous, Secure Backend
"""

import logging
import tempfile
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

logging.disable(logging.CRITICAL)

from api.routes import router as analysis_router
from middleware.security import SecurityMiddleware

TEMP_DIR = tempfile.mkdtemp()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/Shutdown lifecycle"""
    yield
    import shutil
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)

app = FastAPI(
    title="Legal Assistant API",
    version="0.1.0",
    lifespan=lifespan
)

# CORS: Allow only Flutter clients (or adjust as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: specify Flutter app domain
    allow_credentials=False,  # Stateless
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)

app.add_middleware(SecurityMiddleware)

app.include_router(analysis_router)

@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="critical",
        access_log=False,
    )