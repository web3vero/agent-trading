'''
i run a local server with deepseek-r1, below is how to call it from your code
'''

from openai import OpenAI


# Easy to modify prompt at the top
PROMPT = "code me a backtest using volume, capitulations and the vwap. Code it in python and send me back the python code. "


# Easy to modify IP at the top
# this changes daily, get inside discord to know when it changes: https://algotradecamp.com
# check the free api keys section of the discord
LAMBDA_IP = "192.222.57.184"  # Just update this when you start a new instance

# Initialize the client with your local server
client = OpenAI(
    api_key="not-needed",
    base_url=f"http://{LAMBDA_IP}:8000/v1"
)

# Make a chat completion request
response = client.chat.completions.create(
    model="deepseek-r1",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": PROMPT},
    ],
    stream=False
)

print(f"🌙 MoonDev's DeepSeek Response:")
print(f"🤖 Prompt: {PROMPT}")
print(f"✨ Response: {response.choices[0].message.content}")