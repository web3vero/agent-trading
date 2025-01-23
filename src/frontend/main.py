from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, StreamingResponse
from fastapi.encoders import jsonable_encoder
import uvicorn
from pathlib import Path
import sys
import os
import json
import asyncio
from dotenv import load_dotenv

# Load environment variables
if os.getenv("REPL_ID"):  # Check if running on Repl.it
    # Repl.it secrets are automatically loaded into os.environ
    print("🌙 Running on Repl.it - using secrets")
else:
    # Local development - load from .env
    load_dotenv()
    print("🌙 Running locally - using .env file")

# Verify required environment variables
required_vars = [
    "DEEPSEEK_KEY",
    # Add other required keys here
]

missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    print("❌ Missing required environment variables:", missing_vars)
    print("Please set these in .env file (local) or Secrets (Repl.it)")
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

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the home page"""
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "Moon Dev's RBI Agent 🌙"}
    )

@app.post("/analyze")
async def analyze_strategy(links: str = Form(...)):
    """Process trading strategy links"""
    try:
        # Split links by newline or comma
        links_list = [link.strip() for link in links.replace('\n', ',').split(',') if link.strip()]
        results = []
        
        for i, link in enumerate(links_list, 1):
            print(f"🌙 Processing Strategy {i}: {link}")
            
            # Get the latest strategy and backtest files
            strategy_dir = PROJECT_ROOT / "data/rbi/research"
            backtest_dir = PROJECT_ROOT / "data/rbi/backtests_final"
            
            # Process the strategy
            process_trading_idea(link)
            
            # Get the most recent files
            strategy_files = sorted(strategy_dir.glob("strategy_*.txt"), key=lambda x: x.stat().st_mtime, reverse=True)
            backtest_files = sorted(backtest_dir.glob("backtest_final_*.py"), key=lambda x: x.stat().st_mtime, reverse=True)
            
            if strategy_files and backtest_files:
                # Read the strategy and backtest content
                with open(strategy_files[0], 'r') as f:
                    strategy_content = f.read()
                with open(backtest_files[0], 'r') as f:
                    backtest_content = f.read()
                
                result = {
                    "strategy_number": i,
                    "link": link,
                    "strategy": strategy_content,
                    "backtest": backtest_content,
                    "strategy_file": str(strategy_files[0].name),
                    "backtest_file": str(backtest_files[0].name),
                    "status": "success"
                }
            else:
                result = {
                    "strategy_number": i,
                    "link": link,
                    "error": "Strategy processing completed but couldn't find output files",
                    "status": "error"
                }
            
            results.append(result)
            print(f"🚀 Strategy {i} complete!")
            
        return JSONResponse({
            "status": "success",
            "results": results
        })
            
    except Exception as e:
        print(f"❌ Error in analyze endpoint: {str(e)}")
        return JSONResponse({
            "status": "error",
            "message": f"❌ Error: {str(e)}"
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

if __name__ == "__main__":
    # Create required directories if they don't exist
    (FRONTEND_DIR / "static" / "css").mkdir(parents=True, exist_ok=True)
    (FRONTEND_DIR / "static" / "js").mkdir(parents=True, exist_ok=True)
    (FRONTEND_DIR / "static" / "images").mkdir(parents=True, exist_ok=True)
    (FRONTEND_DIR / "templates").mkdir(parents=True, exist_ok=True)
    
    print("🌙 Moon Dev's RBI Agent Frontend Starting...")
    print(f"📁 Frontend Directory: {FRONTEND_DIR}")
    print(f"📁 Static Files: {FRONTEND_DIR / 'static'}")
    print(f"📁 Templates: {FRONTEND_DIR / 'templates'}")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 