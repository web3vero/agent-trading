from fastapi import FastAPI, Request, Form, BackgroundTasks
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.encoders import jsonable_encoder
import uvicorn
from pathlib import Path
import sys
import os
import json
from dotenv import load_dotenv
import datetime

# Load environment variables
load_dotenv()

# Verify required environment variables
required_vars = [
    "DEEPSEEK_KEY",
    "PORT"  # Heroku provides PORT
]

missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    print("❌ Missing required environment variables:", missing_vars)
    print("Please set these in your .env file or Heroku config vars")
    sys.exit(1)

print("✅ All required environment variables found!")

# Get the current directory
FRONTEND_DIR = Path(__file__).parent
PROJECT_ROOT = FRONTEND_DIR.parent

# Add src directory to Python path
sys.path.append(str(PROJECT_ROOT))

from agents.rbi_agent import process_trading_idea

app = FastAPI(
    title="Moon Dev's RBI Agent 🌙",
    description="Research-Backtest-Implement Trading Strategies with AI",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR / "static")), name="static")

# Templates
templates = Jinja2Templates(directory=str(FRONTEND_DIR / "templates"))

# Global variable to store results
processing_results = []
is_processing_complete = False

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the home page"""
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "Moon Dev's RBI Agent 🌙"}
    )

async def process_strategy_background(links: list):
    """Process strategies in the background"""
    global processing_results, is_processing_complete
    
    # Clear old results
    processing_results = []
    is_processing_complete = False
    
    try:
        # Process each strategy
        for i, link in enumerate(links, 1):
            print(f"🌙 Processing Strategy {i}: {link}")
            try:
                # Clear old files
                print("🧹 Clearing old files...")
                strategy_dir = Path("data/rbi/research")
                backtest_dir = Path("data/rbi/backtests_final")
                
                # Process the strategy
                process_trading_idea(link)
                
                # Get the most recent strategy and backtest files
                strategy_files = list(strategy_dir.glob("*.txt"))
                backtest_files = list(backtest_dir.glob("*.py"))
                
                if strategy_files and backtest_files:
                    strategy_file = max(strategy_files, key=lambda x: x.stat().st_mtime)
                    backtest_file = max(backtest_files, key=lambda x: x.stat().st_mtime)
                    
                    strategy_content = strategy_file.read_text()
                    backtest_content = backtest_file.read_text()
                    
                    result = {
                        "strategy_number": i,
                        "link": link,
                        "status": "success",
                        "strategy": strategy_content,
                        "backtest": backtest_content,
                        "strategy_file": strategy_file.name,
                        "backtest_file": backtest_file.name
                    }
                    processing_results.append(result)
                    print(f"✅ Strategy {i} complete!")
                else:
                    result = {
                        "strategy_number": i,
                        "link": link,
                        "status": "error",
                        "message": "Strategy processing completed but output files not found"
                    }
                    processing_results.append(result)
                    print(f"❌ Strategy {i} failed: Output files not found")
            except Exception as e:
                result = {
                    "strategy_number": i,
                    "link": link,
                    "status": "error",
                    "message": str(e)
                }
                processing_results.append(result)
                print(f"❌ Strategy {i} failed: {str(e)}")
    finally:
        is_processing_complete = True

@app.post("/analyze")
async def analyze_strategy(request: Request, background_tasks: BackgroundTasks):
    form = await request.form()
    links = form.get("links", "").split("\n")
    links = [link.strip() for link in links if link.strip()]
    
    if not links:
        return JSONResponse({"status": "error", "message": "No links provided"})
    
    # Start processing in background
    background_tasks.add_task(process_strategy_background, links)
    
    return JSONResponse({
        "status": "success",
        "message": "Analysis started"
    })

@app.get("/download/strategy/{filename}")
async def download_strategy(filename: str):
    """Download a strategy file"""
    file_path = PROJECT_ROOT / "data/rbi/research" / filename
    if file_path.exists():
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="text/plain"
        )
    return JSONResponse({
        "status": "error",
        "message": "File not found"
    })

@app.get("/download/backtest/{filename}")
async def download_backtest(filename: str):
    """Download a backtest file"""
    file_path = PROJECT_ROOT / "data/rbi/backtests_final" / filename
    if file_path.exists():
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="text/plain"
        )
    return JSONResponse({
        "status": "error",
        "message": "File not found"
    })

@app.get("/results")
async def get_results():
    """Get current processing results"""
    return JSONResponse({
        "status": "success",
        "results": processing_results,
        "is_complete": is_processing_complete
    })

if __name__ == "__main__":
    # Get port from environment variable (Heroku sets this)
    port = int(os.getenv("PORT", 8000))
    
    print("🌙 Moon Dev's RBI Agent Starting...")
    print(f"📁 Frontend Directory: {FRONTEND_DIR}")
    print(f"📁 Static Files: {FRONTEND_DIR / 'static'}")
    print(f"📁 Templates: {FRONTEND_DIR / 'templates'}")
    
    # Start server with host 0.0.0.0 for Heroku
    uvicorn.run("main:app", host="0.0.0.0", port=port) 