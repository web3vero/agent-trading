'''
BELOW IS HOW TO SET UP DEEPSEEK R1 ON LAMBDA LABS
THERE IS ANOTHER FILE CALLED DEEPSEEK_LOCAL_CALL.PY THAT IS HOW TO CALL IT FROM YOUR COMPUTER
WHILE I STREAM I WILL LIKELY HAVE THIS API RUNNING ON LAMBDA LABS SO EVERYONE CAN USE IT
THE IP WILL CHANGE DAILY, CHECK DISCORD TO KNOW WHEN IT CHANGES: https://algotradecamp.com


# available free while moon dev is streaming: https://www.youtube.com/@moondevonyt 



Running DeepSeek-R1 70B using Ollama#
Introduction#
This short tutorial teaches how to use a Lambda Cloud on-demand instance to run the DeepSeek-R1 70B model using Ollama in a Docker container. Since NVIDIA Container Toolkit is preinstalled as part of Lambda Stack on all on-demand instances, Docker containers can use the GPUs without any additional configuration.

Prerequisites#
For this tutorial, it's recommended that you use an instance type with more than 40 GB of VRAM, for example, a 1x GH200 or 1x H100.

Download Ollama and start the Ollama server#
Log into your instance using SSH or by opening a terminal in Jupyter Lab.

Download Ollama and start the Ollama server:


sudo docker run -d --gpus=all -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
The download is complete once you see:


Status: Downloaded newer image for ollama/ollama:latest
Confirm the Ollama server is running:


sudo docker ps
You should see output similar to:


CONTAINER ID   IMAGE           COMMAND               CREATED       STATUS       PORTS                                           NAMES
3b27fdfbbfcc   ollama/ollama   "/bin/ollama serve"   2 hours ago   Up 2 hours   0.0.0.0:11434->11434/tcp, :::11434->11434/tcp   ollama
Download and run the DeepSeek-R1 70B model#
Download and run the DeepSeek-R1 70B model:


sudo docker exec -it ollama ollama run deepseek-r1:70b
The model is over 40 GB in size and can take 10-15 minutes to download.

The model is running when you see:

success
>>> Send a message (/? for help)
Test the DeepSeek-R1 70B model#
Test the DeepSeek-R1 70B model by submitting a prompt, for example:


What is the national anthem of France?
You should see output similar to:
'''

from fastapi import FastAPI, HTTPException
import requests
import json

app = FastAPI(title="MoonDev's DeepSeek API 🌙")

# Configuration
OLLAMA_BASE_URL = "http://localhost:11434"

@app.get("/health")
async def health_check():
    try:
        # Test Ollama connection
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags")
        if response.status_code == 200:
            return {"status": "healthy", "message": "✨ Ollama is healthy and responding!"}
        else:
            return {"status": "unhealthy", "message": "❌ Ollama is not responding correctly"}
    except Exception as e:
        return {"status": "error", "message": f"❌ Error connecting to Ollama: {str(e)}"}

@app.post("/v1/chat/completions")
async def create_chat_completion(request: dict):
    print(f"🤖 Received chat request for model: {request.get('model', 'unknown')}")
    print(f"💬 Messages: {request.get('messages', [])}")
    
    try:
        # Test Ollama connection first
        print("🔍 Testing Ollama connection...")
        test_response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        print(f"📡 Ollama Test Response: {test_response.status_code}")
        
        # Just use the last user message
        messages = request.get('messages', [])
        prompt = messages[-1]['content']  # Get just the user's question
        
        print(f"🎯 Sending to Ollama URL: {OLLAMA_BASE_URL}")
        print(f"📝 Prompt: {prompt}")
        
        payload = {
            "model": "deepseek-r1:70b",
            "prompt": prompt,
            "stream": False
        }
        
        print("🌟 Sending request to Ollama...")
        print(f"📦 Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=120  # Increased timeout
        )
        
        print(f"📡 Ollama Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✨ Success! Response: {json.dumps(result, indent=2)}")
            return {
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": result.get("response", "")
                    }
                }]
            }
        else:
            print(f"❌ Error from Ollama: {response.text}")
            raise HTTPException(status_code=response.status_code, detail="Failed to generate response")
            
    except requests.Timeout:
        print("⏰ Request timed out waiting for Ollama")
        raise HTTPException(status_code=504, detail="Request timed out")
    except requests.ConnectionError:
        print("🔌 Connection error reaching Ollama")
        raise HTTPException(status_code=502, detail="Cannot connect to Ollama")
    except Exception as e:
        print(f"❌ Error generating response: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting MoonDev's DeepSeek API...")
    uvicorn.run(app, host="0.0.0.0", port=8000)