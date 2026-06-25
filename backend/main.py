from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1 import chat

app = FastAPI(
    title="DocuMind AI Core API",
    description="Multi-tenant Enterprise Documentation AI SaaS",
    version="1.0.0"
)

# CORS Configuration for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "DocuMind Core API"}

@app.get("/")
async def root():
    return {"message": "Welcome to the DocuMind API"}
