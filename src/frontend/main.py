from fastapi import FastAPI, Request, Form
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
        print("🌙 Starting strategy analysis...")
        
        # Create required directories
        for dir_path in [
            PROJECT_ROOT / "data",
            PROJECT_ROOT / "data/rbi",
            PROJECT_ROOT / "data/rbi/research",
            PROJECT_ROOT / "data/rbi/backtests",
            PROJECT_ROOT / "data/rbi/backtests_final"
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"📁 Ensuring directory exists: {dir_path}")
        
        # Split links by newline or comma
        links_list = [link.strip() for link in links.replace('\n', ',').split(',') if link.strip()]
        print(f"🔍 Processing {len(links_list)} links: {links_list}")
        
        results = []
        
        for i, link in enumerate(links_list, 1):
            try:
                print(f"🌙 Processing Strategy {i}: {link}")
                
                # Get the latest strategy and backtest files
                strategy_dir = PROJECT_ROOT / "data/rbi/research"
                backtest_dir = PROJECT_ROOT / "data/rbi/backtests_final"
                
                # Process the strategy
                process_trading_idea(link)
                
                # Get the most recent files
                strategy_files = sorted(strategy_dir.glob("strategy_*.txt"), key=lambda x: x.stat().st_mtime, reverse=True)
                backtest_files = sorted(backtest_dir.glob("backtest_final_*.py"), key=lambda x: x.stat().st_mtime, reverse=True)
                
                print(f"Found {len(strategy_files)} strategy files and {len(backtest_files)} backtest files")
                
                if strategy_files and backtest_files:
                    print(f"📄 Found files: {strategy_files[0].name}, {backtest_files[0].name}")
                    try:
                        # Read the strategy and backtest content
                        with open(strategy_files[0], 'r') as f:
                            strategy_content = f.read()
                            print(f"✅ Successfully read strategy file: {len(strategy_content)} characters")
                        with open(backtest_files[0], 'r') as f:
                            backtest_content = f.read()
                            print(f"✅ Successfully read backtest file: {len(backtest_content)} characters")
                        
                        result = {
                            "strategy_number": i,
                            "link": link,
                            "strategy": strategy_content,
                            "backtest": backtest_content,
                            "strategy_file": str(strategy_files[0].name),
                            "backtest_file": str(backtest_files[0].name),
                            "status": "success"
                        }
                        print("✅ Successfully created result object")
                    except Exception as e:
                        print(f"❌ Error reading files: {str(e)}")
                        result = {
                            "strategy_number": i,
                            "link": link,
                            "error": f"Error reading output files: {str(e)}",
                            "status": "error"
                        }
                else:
                    print(f"❌ No output files found for strategy {i}")
                    result = {
                        "strategy_number": i,
                        "link": link,
                        "error": "Strategy processing completed but couldn't find output files",
                        "status": "error"
                    }
                
                results.append(result)
                print(f"🚀 Strategy {i} complete!")
            except Exception as e:
                print(f"❌ Error processing strategy {i}: {str(e)}")
                results.append({
                    "strategy_number": i,
                    "link": link,
                    "error": f"Error processing strategy: {str(e)}",
                    "status": "error"
                })
        
        print("Preparing response with results...")
        response_data = {
            "status": "success",
            "results": results
        }
        print(f"Response data prepared: {len(results)} results")
        return JSONResponse(response_data)
            
    except Exception as e:
        error_msg = f"❌ Error in analyze endpoint: {str(e)}"
        print(error_msg)
        return JSONResponse({
            "status": "error",
            "message": error_msg
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
    # Get port from environment variable (Heroku sets this)
    port = int(os.getenv("PORT", 8000))
    
    print("🌙 Moon Dev's RBI Agent Starting...")
    print(f"📁 Frontend Directory: {FRONTEND_DIR}")
    print(f"📁 Static Files: {FRONTEND_DIR / 'static'}")
    print(f"📁 Templates: {FRONTEND_DIR / 'templates'}")
    
    # Start server with host 0.0.0.0 for Heroku
    uvicorn.run("main:app", host="0.0.0.0", port=port) 