from fastapi import FastAPI
from backend.api import routes_ingestion
from backend.api import routes_rag
from backend.api import routes_study

app = FastAPI(
    title="Material Ingestion, Study Planning, and Intelligence API",
    description="API for multimodal file ingestion, RAG, concept graphs, and structured intelligent workflows.",
    version="2.0.0"
)

# Register decoupled Routers
app.include_router(routes_ingestion.router)
app.include_router(routes_rag.router)
app.include_router(routes_study.router)

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Engine running actively."}

if __name__ == "__main__":
    import uvicorn
    # Make sure to run from root using: python -m backend.main
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
