import os
import time
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

# Setup in-memory caching
caches.set_config({"default": {"cache": "aiocache.SimpleMemoryCache"}})

# Setup logging
logger.add("app.log", rotation="10MB", retention="7 days", level="INFO", format="{time} {level} {message}")

# Initialize FastAPI
app = FastAPI(
    title="Pydantic Microservice API",
    description="This API provides microservices for handling Pydantic models dynamically.",
    version="1.0.0",
    docs_url="/docs",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1}
)

# API Key Auth
API_KEY = os.getenv("KEY_API")
API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def verify_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized: Invalid API Key")
    return api_key

# API Key check middleware
@app.middleware("http")
async def api_key_middleware(request: Request, call_next):
    api_key = request.headers.get(API_KEY_NAME)
    if api_key != API_KEY:
        return JSONResponse(status_code=403, content={"detail": "Unauthorized: Invalid API Key"})
    return await call_next(request)

# Request logging with performance timing
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.perf_counter()
    logger.info(f"🔍 Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    logger.info(f"✅ Completed {request.method} {request.url} in {process_time:.4f}s")
    response.headers["X-Process-Time"] = str(round(process_time, 4))
    return response

# Exception handler
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourfrontend.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["X-API-KEY", "Content-Type"],
)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(HTTPException, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Load models from generated files
async def load_model(model_file):
    try:
        logger.info(f"Loading model from: {model_file.name}")
        module_name = model_file.stem
        spec = importlib.util.spec_from_file_location(module_name, model_file)
        module = importlib.util.module_from_spec(spec)
        await asyncio.to_thread(spec.loader.exec_module, module)
        return module
    except Exception as e:
        logger.error(f"❌ Failed to load model {model_file.name}: {e}")
        return None

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
        if not module:
            continue
        for attr_name in dir(module):
            try:
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, BaseModel) and attr is not BaseModel:
                    models[attr_name] = attr
            except Exception as e:
                logger.warning(f"⚠️ Skipping attribute {attr_name}: {e}")

    logger.info(f"✅ Loaded models: {list(models.keys())}")
    return models

# Include all microservice routers
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
            else:
                logger.warning(f"⚠️ No router found in {service_name}")
        except Exception as e:
            logger.error(f"❌ Failed to include {service_name}: {e}")

generated_models = {}

# On app startup
@app.on_event("startup")
async def startup_event():
    global generated_models
    start_time = time.perf_counter()
    logger.info("🚀 Startup: Loading models & services...")
    try:
        generated_models = await load_generated_models()
        await include_microservices(app)
        logger.info("✅ Startup complete! API is ready.")
    except Exception as e:
        logger.critical(f"🔥 Fatal error during startup: {e}")
    finally:
        duration = time.perf_counter() - start_time
        logger.info(f"📊 Startup completed in {duration:.2f} seconds.")

# Routes
@app.get("/")
def root():
    return {"message": "Welcome to the Pydantic Microservice!"}

@app.get("/models", dependencies=[Depends(verify_api_key)],
         summary="List all available models",
         description="Returns a list of all dynamically loaded Pydantic models.")
@limiter.limit("10/minute")
@cached(ttl=60)
async def list_models(request: Request):
    logger.info("📜 Listing models")
    if generated_models is None:
        raise HTTPException(status_code=503, detail="Service Unavailable: Models not loaded yet")
    return {"models": list(generated_models.keys())}

@app.get("/models/{model_name}", dependencies=[Depends(verify_api_key)],
         summary="Get schema of a specific model",
         description="Fetch the JSON schema of a specific Pydantic model.")
@limiter.limit("10/minute")
@cached(ttl=60)
async def get_model(request: Request, model_name: str):
    logger.info(f"🔎 Requested model name: {model_name}")
    if generated_models is None:
        raise HTTPException(status_code=503, detail="Service Unavailable: Models not loaded yet")
    if model_name in generated_models:
        return generated_models[model_name].schema()
    else:
        raise HTTPException(status_code=404, detail=f"Model {model_name} not found")
