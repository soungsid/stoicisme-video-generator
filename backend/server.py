from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

# Import database
from database import connect_to_mongo, close_mongo_connection

# Import routes
from routes import ideas, scripts, audio, videos, youtube_routes, config, pipeline

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    print("✅ Connected to MongoDB Atlas")
    yield
    # Shutdown
    await close_mongo_connection()
    print("❌ Disconnected from MongoDB Atlas")

app = FastAPI(
    title="YouTube Video Generator API",
    description="API for automated YouTube video generation with Stoicism content",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "YouTube Video Generator API is running"}

# Register routes
app.include_router(ideas.router, prefix="/api/ideas", tags=["Ideas"])
app.include_router(scripts.router, prefix="/api/scripts", tags=["Scripts"])
app.include_router(audio.router, prefix="/api/audio", tags=["Audio"])
app.include_router(videos.router, prefix="/api/videos", tags=["Videos"])
app.include_router(youtube_routes.router, prefix="/api/youtube", tags=["YouTube"])
app.include_router(config.router, prefix="/api/config", tags=["Configuration"])
app.include_router(pipeline.router, prefix="/api/pipeline", tags=["Pipeline"])

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("BACKEND_PORT", 8001))
    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    uvicorn.run("server:app", host=host, port=port, reload=True)
