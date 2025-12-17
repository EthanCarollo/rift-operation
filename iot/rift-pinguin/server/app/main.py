from fastapi import FastAPI
from app.controllers.websocket_controller import router as websocket_router
from app.services.kyutai_service import kyutai_service
import contextlib

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # Load model on startup
    kyutai_service.load_model()
    yield
    # Clean up if needed

app = FastAPI(lifespan=lifespan)

app.include_router(websocket_router)

@app.get("/")
def read_root():
    return {"status": "ok", "service": "Kyutai ASR Server"}
