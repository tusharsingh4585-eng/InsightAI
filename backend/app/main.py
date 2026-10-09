from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router

app = FastAPI(
    title="InsightAI API",
    version="1.0.0",
    description="AI-powered business intelligence backend"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router, prefix="/api")

@app.get("/")
def root():
    return {"message": "InsightAI API is running", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "healthy"}
