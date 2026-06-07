import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import notes
from bot import setup_application

logger = logging.getLogger(__name__)

# Initialize bot app
bot_app = setup_application()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Cek apakah bot di-disable via environment variable (misal untuk testing API saja)
    run_bot = os.getenv("START_BOT", "true").lower() == "true"
    
    if run_bot:
        logger.info("Initializing Telegram Bot...")
        await bot_app.initialize()
        await bot_app.start()
        logger.info("Starting Telegram Bot polling...")
        await bot_app.updater.start_polling(allowed_updates=["message"])
    else:
        logger.info("Telegram Bot is disabled via START_BOT env var.")

    yield

    if run_bot:
        logger.info("Stopping Telegram Bot...")
        await bot_app.updater.stop()
        await bot_app.stop()
        await bot_app.shutdown()


app = FastAPI(
    title="Second Brain API",
    description="API for Second Brain, running alongside Telegram Bot",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ganti dengan origin yang spesifik di production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(notes.router, prefix="/api/v1/notes", tags=["Notes"])


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


@app.get("/health")
async def health_check():
    bot_running = False
    if bot_app.updater:
        bot_running = bot_app.updater.running
        
    return {
        "status": "ok",
        "bot_running": bot_running
    }
