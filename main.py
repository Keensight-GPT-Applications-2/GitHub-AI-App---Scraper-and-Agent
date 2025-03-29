import os
import asyncio
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from pathlib import Path
import importlib.util
from importlib import import_module
from pydantic import BaseModel
from aiocache.decorators import cached
from loguru import logger
from aiocache import caches, SimpleMemoryCache

caches.set_config({"default": {"cache": "aiocache.SimpleMemoryCache"}})

# ✅ Configure Loguru for structured logging
logger.add("app.log", rotation="10MB", retention="7 days", level="INFO", format="{time} {level} {message}")

# ✅ FastAPI app initialization
app = FastAPI(
    title="Pydantic Microservice API",
    description="This API provides microservices for handling Pydantic models dynamically.",
    version="1.0.0",
    docs_url="/docs",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1}  # Hide schemas by default
)

# ✅ Initialize Cache
cache = SimpleMemoryCache()

# ✅ API Key Authentication
API_KEY = os.getenv("KEY_API")  # Set this in your .env file
API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def verify_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized: Invalid API Key")
    return api_key

@app.middleware("http")
async def api_key_middleware(request: Request, call_next):
    api_key = request.headers.get(API_KEY_NAME)

    # Debugging: Print received and expected API key
    print(f"🔑 Received API Key: {api_key}")
    print(f"✅ Expected API Key: {API_KEY}")

    if api_key != API_KEY:
        return JSONResponse(status_code=403, content={"detail": "Unauthorized: Invalid API Key"})

    return await call_next(request)

# ✅ Rate Limiting (10 requests per minute per IP)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(HTTPException, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# ✅ CORS Middleware (Allow only trusted domains)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourfrontend.com"],  # Update this with your actual frontend domain
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["X-API-KEY", "Content-Type"],
)

# ✅ Request Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"🔍 Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    return response

# ✅ Exception Handling (User-friendly errors)
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

# ✅ Load Pydantic Models (Async)
async def load_model(model_file):
    logger.info(f"Loading model from: {model_file.name}")
    module_name = model_file.stem
    spec = importlib.util.spec_from_file_location(module_name, model_file)
    module = importlib.util.module_from_spec(spec)
    await asyncio.to_thread(spec.loader.exec_module, module)
    return module

async def load_generated_models():
    models = {}
    models_dir = Path(__file__).resolve().parent / "models/generated_models"

    if not models_dir.exists():
        logger.error("❌ Generated models directory does not exist.")
        return models

    model_files = list(models_dir.glob("*.py"))
    logger.info(f"🔄 Found {len(model_files)} model files")

    loaded_modules = await asyncio.gather(*(load_model(file) for file in model_files))

    for module in loaded_modules:
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and issubclass(attr, BaseModel) and attr is not BaseModel:
                models[attr_name] = attr

    logger.info(f"✅ Loaded models: {list(models.keys())}")
    return models

# ✅ Include all microservices dynamically (Async)
async def include_microservices(app):
    microservices_dir = Path(__file__).resolve().parent / "microservices"

    if not microservices_dir.exists():
        logger.error("❌ Microservices directory does not exist.")
        return

    service_files = list(microservices_dir.glob("*.py"))
    logger.info(f"🛠️ Found microservices: {[s.stem for s in service_files]}")

    for service_file in service_files:
        service_name = service_file.stem
        try:
            logger.info(f"Including service: {service_name}")
            module = import_module(f"microservices.{service_name}")
            if hasattr(module, "router"):
                app.include_router(module.router)
        except Exception as e:
            logger.error(f"❌ Failed to include service {service_name}: {e}")

generated_models = {}  # ✅ Initialize it with an empty dictionary  

# ✅ Asynchronous Startup Events
@app.on_event("startup")
async def startup_event():
    global generated_models
    logger.info("🚀 Application startup: Loading models and microservices...")
    generated_models = await load_generated_models()
    await include_microservices(app)
    logger.info("✅ Startup complete! API is ready.")


# ✅ API Endpoints
@app.get("/")
def root():
    return {"message": "Welcome to the Pydantic Microservice!"}

@app.get("/models", dependencies=[Depends(verify_api_key)], 
         summary="List all available models",
         description="Returns a list of all dynamically loaded Pydantic models.")
@limiter.limit("10/minute")
@cached(ttl=60)
async def list_models(request: Request):
    """
    Fetch all available models that have been dynamically loaded.
    This helps in understanding which models are available for API usage.
    """
    logger.info("📜 Listing models")
    if generated_models is None:
        raise HTTPException(status_code=503, detail="Service Unavailable: Models not loaded yet")  # ✅ Handle missing models
    return {"models": list(generated_models.keys())}


@app.get("/models/{model_name}", dependencies=[Depends(verify_api_key)], 
         summary="Get schema of a specific model",
         description="Fetch the JSON schema of a specific Pydantic model.")
@limiter.limit("10/minute")
@cached(ttl=60)
async def get_model(request: Request, model_name: str):
    """
    Retrieve the JSON schema of a Pydantic model by name.
    This helps in structuring API inputs for validation.
    """
    logger.info(f"🔎 Requested model name: {model_name}")
    if generated_models is None:
        raise HTTPException(status_code=503, detail="Service Unavailable: Models not loaded yet")  # ✅ Handle missing models
    if model_name in generated_models:
        return generated_models[model_name].schema()
    else:
        raise HTTPException(status_code=404, detail=f"Model {model_name} not found")
