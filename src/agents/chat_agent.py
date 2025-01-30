"""
🌙 Moon Dev's Chat Agent
Built with love by Moon Dev 🚀

This agent monitors YouTube stream chat and answers questions using a knowledge base.
"""

import sys
from pathlib import Path
# Add project root to Python path for imports
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

import os
import time
from datetime import datetime
from termcolor import cprint
from dotenv import load_dotenv
import pandas as pd
from src.config import *
from src.models import model_factory
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
import threading
import shutil
import itertools
import random
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import base64
from PIL import Image
import io

# Load environment variables from the project root
env_path = Path(project_root) / '.env'
if not env_path.exists():
    raise ValueError(f"🚨 .env file not found at {env_path}")

load_dotenv(dotenv_path=env_path)

# Model override settings
MODEL_TYPE = "groq"  # Using Claude for chat responses
MODEL_NAME = "llama-3.3-70b-versatile"  # Fast, efficient model

# Configuration
SELENIUM_AS_DEFAULT = True  # Skip API and use Selenium directly when True
CHECK_INTERVAL = 30.0  # API chat check interval
SELENIUM_CHECK_INTERVAL = 5.0  # Selenium chat check interval (faster since no quota)
LIVE_CHECK_INTERVAL = 900.0  # Live stream check every 15 minutes
SELENIUM_LIVE_CHECK_INTERVAL = 60.0  # Selenium live stream check interval
USE_FALLBACK = True  # Enable Selenium fallback when API quota exceeded
MAX_RESPONSE_TIME = 5.0  # Maximum time to spend generating a response
CONFIDENCE_THRESHOLD = 0.8  # Minimum confidence to answer a question
MAX_RETRIES = 3  # Maximum number of retries for API calls
MAX_RESPONSE_TOKENS = 150  # Maximum number of tokens in response
CHAT_MEMORY_SIZE = 30  # Number of recent chat messages to keep in memory
MIN_CHARS_FOR_RESPONSE = 10  # Minimum characters needed in message to get a response
DEFAULT_INITIAL_CHATS = 10  # Default number of initial chats to process

# Moon Dev's YouTube Channel ID
YOUTUBE_CHANNEL_ID = "UCN7D80fY9xMYu5mHhUhXEFw"  # Replace with your channel ID

# Chat prompts
CHAT_PROMPT = """You are Moon Dev's Chat AI Agent. Your task is to answer questions from YouTube stream chat.
Use the provided knowledge base to ensure accurate answers about Moon Dev's projects and preferences.

Consider:
- Only answer if you're confident (above {confidence_threshold})
- Keep responses concise but friendly
- Always include emojis in responses
- Reference Moon Dev's style and personality
- If unsure, respond with "I'll let Moon Dev answer that one! 🌙"

Knowledge Base:
{knowledge_base}

Question: {question}

Respond in this format:
CONFIDENCE: X.XX
RESPONSE: Your response here with emojis

IF THE CHAT IS NOT IN ENGLISH, TRANSLATE THE CHAT IN YOUR RESPONSE AND SEND THAT BACK AS FIRST MESSAGE, THEN RESPOND IN THEIR LANGUAGE AND THEN TRANSLATE THAT TO ENGLISH.
"""

NEGATIVITY_CHECK_PROMPT = """You are a content moderator. Analyze this message for negativity, toxicity, or harmful content.
Consider hate speech, insults, excessive profanity, threats, or any form of harmful behavior.

Message: {message}

Rate the negativity from 0.0 to 1.0 where:
0.0 = Completely positive/neutral
1.0 = Extremely negative/toxic

Respond with only a number between 0.0 and 1.0.
"""

PROMPT_777 = """You are a spiritual guide for entrepreneurs and builders. 
Someone just sent "777" in the chat, which is a sign good vibrations and blessings.

Generate an inspiring Bible verse and brief interpretation that would motivate entrepreneurs, developers, and builders to:
- Keep working hard on their projects
- Trust in the divine timing of their success
- Stay focused on their goals
- Build with purpose and love

The verse should feel personal and relevant to someone building something meaningful.
Keep the total response under 100 words and include the verse reference.

Format your response as a single line with the verse, reference, and a very brief (10 words or less) interpretation.
"""

# Configuration
NEGATIVITY_THRESHOLD = 0.7  # Messages rated above this are considered negative

# Add new constants for emojis
USER_EMOJIS = ["👨🏽", "👩🏽", "🧑🏽‍🦱", "👨🏽‍🦱", "👨🏽‍🦳", "👱🏽‍♂️", "👨🏽‍🦰", "👩🏽‍🦱"]
AI_EMOJIS = ["🤖", "🐳", "🐐", "👽", "🧠", "🌚"]
CLOWN_SPAM = "🤡" * 5  # 9 clown emojis for negative messages

# Add lucky emojis for 777 responses
LUCKY_EMOJIS = ["⭐️", "🧠", "😎", "♥️", "💙", "💚", "😇", "🌟", "✨", "💫", "❤️‍🔥"]

# Configuration
QUOTA_BACKOFF_BASE = 2  # Base for exponential backoff
QUOTA_BACKOFF_MAX = 3600  # Maximum backoff of 1 hour

class ChatScraper:
    """Fallback scraper for when API quota is exceeded"""
    def __init__(self):
        """Initialize the scraper with robust Chrome options"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless=new")  # Updated headless mode
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-notifications")
            chrome_options.add_argument("--disable-popup-blocking")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-infobars")
            chrome_options.add_argument("--remote-debugging-port=9222")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            cprint("🚀 Initializing Chrome driver with enhanced options...", "cyan")
            self.driver = webdriver.Chrome(options=chrome_options)
            self.last_messages = set()
            cprint("✅ Chrome driver initialized successfully!", "green")
        except Exception as e:
            cprint(f"❌ Error initializing Chrome driver: {str(e)}", "red")
            raise
        
    def get_live_stream_url(self, channel_id):
        """Get the current live stream URL with enhanced error handling"""
        try:
            channel_url = f"https://www.youtube.com/channel/{channel_id}/live"
            cprint(f"🔍 Navigating to: {channel_url}", "cyan")
            
            self.driver.get(channel_url)
            time.sleep(5)  # Give page time to load
            
            # Wait for either chat or a specific element that indicates no live stream
            try:
                chat_present = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "yt-live-chat-app, #content"))
                )
                
                # Check if we're actually on a live stream
                current_url = self.driver.current_url
                if "/live" in current_url or "/watch" in current_url:
                    cprint(f"✨ Found live stream!", "green")
                    return current_url
                else:
                    cprint("❌ Channel is not live", "yellow")
                    return None
                    
            except selenium.common.exceptions.TimeoutException:
                cprint("⏳ Timed out waiting for live stream elements", "yellow")
                return None
                
        except Exception as e:
            cprint(f"❌ Error getting live stream URL: {str(e)}", "red")
            # Try to recover by reinitializing the driver
            try:
                self.driver.quit()
                chrome_options = Options()
                chrome_options.add_argument("--headless=new")
                chrome_options.add_argument("--no-sandbox")
                self.driver = webdriver.Chrome(options=chrome_options)
            except:
                pass
            return None
            
    def get_chat_messages(self):
        """Scrape chat messages using Selenium with improved selectors"""
        try:
            # Wait for chat frame to be present
            chat_frame = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "iframe#chatframe"))
            )
            
            # Switch to chat frame
            self.driver.switch_to.frame(chat_frame)
            
            # Wait for chat container with better selector
            chat_container = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "yt-live-chat-item-list-renderer"))
            )
            
            # Get all message elements with more specific selector
            all_messages = chat_container.find_elements(By.CSS_SELECTOR, "#items yt-live-chat-text-message-renderer")
            
            # Process messages - get all new ones since last check
            new_messages = []
            
            # If this is first run, get exactly DEFAULT_INITIAL_CHATS messages from the end
            if not self.last_messages:  # If this is first run
                messages_to_process = all_messages[-DEFAULT_INITIAL_CHATS:] if len(all_messages) > DEFAULT_INITIAL_CHATS else all_messages
                cprint(f"📥 Found {len(messages_to_process)} initial messages", "cyan")
            else:
                # Otherwise just check last few for new ones
                messages_to_process = all_messages[-5:]  # Check last 5 for new messages
                
            for msg in messages_to_process:
                try:
                    author = msg.find_element(By.CSS_SELECTOR, "#author-name").text
                    content = msg.find_element(By.CSS_SELECTOR, "#message").text
                    msg_id = f"{author}:{content}"
                    
                    if msg_id not in self.last_messages:
                        self.last_messages.add(msg_id)
                        new_messages.append({
                            'user': author,
                            'message': content,
                            'timestamp': datetime.now()
                        })
                        
                        # Keep set size manageable
                        if len(self.last_messages) > 100:
                            self.last_messages.clear()
                except Exception as e:
                    cprint(f"⚠️ Error processing message: {str(e)}", "yellow")
                    continue
            
            # Switch back to default content
            self.driver.switch_to.default_content()
            return new_messages  # Already in chronological order
            
        except Exception as e:
            cprint(f"❌ Error scraping chat: {str(e)}", "red")
            try:
                self.driver.switch_to.default_content()
            except:
                pass
            return []
            
    def close(self):
        """Clean up resources"""
        try:
            self.driver.switch_to.default_content()  # Make sure we're out of any frames
            self.driver.quit()
        except:
            pass

class YouTubeChatMonitor:
    def __init__(self, api_key):
        """Initialize YouTube chat monitor"""
        self.api_key = api_key
        self.youtube = build(
            "youtube",
            "v3",
            developerKey=api_key
        )
        self.live_chat_id = None
        self.next_page_token = None
        self.last_message_time = datetime.now()
        self.last_live_check = None
        self.video_id = None
        self.using_fallback = SELENIUM_AS_DEFAULT  # Initialize with default setting
        self.scraper = ChatScraper() if SELENIUM_AS_DEFAULT else None  # Create scraper if using Selenium by default
        
    def _init_fallback(self):
        """Initialize fallback scraper"""
        if not self.scraper and USE_FALLBACK:
            cprint("🔄 API quota exceeded - switching to Selenium fallback...", "yellow")
            self.scraper = ChatScraper()
            self.using_fallback = True
            
    def get_live_chat_id(self, channel_id):
        """Get live chat ID with fallback methods"""
        try:
            # Try API first if not already using fallback
            if not self.using_fallback:
                try:
                    chat_id = self._get_chat_id_api(channel_id)
                    if chat_id:
                        return chat_id
                except HttpError as e:
                    if "quota" in str(e).lower():
                        cprint("\n🔄 YouTube API quota exceeded!", "yellow")
                        cprint("🚀 Switching to Selenium fallback mode...", "cyan")
                        self._init_fallback()
                    else:
                        raise
            
            # Try Selenium fallback
            if self.using_fallback:
                if not self.scraper:
                    self._init_fallback()
                url = self.scraper.get_live_stream_url(channel_id)
                if url:
                    cprint(f"✨ Successfully connected to live stream via Selenium!", "green")
                    cprint(f"🔗 Stream URL: {url[:60]}...", "cyan")
                    return "fallback"
                else:
                    cprint("❌ No live stream found via Selenium", "yellow")
                    
            return None
            
        except Exception as e:
            if "quota" in str(e).lower() and not self.using_fallback:
                cprint("\n🔄 YouTube API quota exceeded!", "yellow")
                cprint("🚀 Switching to Selenium fallback mode...", "cyan")
                self._init_fallback()
                # Retry immediately with fallback
                return self.get_live_chat_id(channel_id)
            else:
                cprint(f"❌ Error getting live chat ID: {str(e)}", "red")
            return None
            
    def get_chat_messages(self):
        """Get chat messages with fallback methods"""
        if not self.using_fallback:
            try:
                return self._get_messages_api()
            except HttpError as e:
                if "quota" in str(e).lower():
                    self._init_fallback()
                else:
                    raise
                    
        if self.using_fallback:
            return self.scraper.get_chat_messages()
            
        return []
        
    def _get_chat_id_api(self, channel_id):
        """Get live chat ID using YouTube API"""
        try:
            # Search for active live stream
            request = self.youtube.search().list(
                part="id",
                channelId=channel_id,
                eventType="live",
                type="video",
                fields="items/id/videoId",
                maxResults=1
            )
            response = request.execute()
            
            if response.get('items'):
                self.video_id = response['items'][0]['id']['videoId']
                cprint(f"✨ Found live stream: {self.video_id}", "cyan")
                
                # Get chat ID for found video
                request = self.youtube.videos().list(
                    part="liveStreamingDetails",
                    id=self.video_id,
                    fields="items/liveStreamingDetails/activeLiveChatId"
                )
                response = request.execute()
                
                if response.get('items'):
                    chat_id = response['items'][0].get('liveStreamingDetails', {}).get('activeLiveChatId')
                    if chat_id:
                        cprint(f"🎯 Found active live chat! ID: {chat_id[:20]}...", "green")
                        return chat_id
                        
            return None
            
        except HttpError as e:
            if "quota" in str(e).lower():
                raise  # Re-raise quota error to trigger fallback
            cprint(f"❌ Error in API chat ID lookup: {str(e)}", "red")
            return None
            
    def _get_messages_api(self):
        """Get messages using YouTube API"""
        if not self.live_chat_id:
            return []
            
        try:
            request = self.youtube.liveChatMessages().list(
                liveChatId=self.live_chat_id,
                part="snippet,authorDetails",
                pageToken=self.next_page_token,
                maxResults=DEFAULT_INITIAL_CHATS  # Use config value instead of hardcoded 3
            )
            response = request.execute()
            
            self.next_page_token = response.get('nextPageToken')
            
            if not response.get('items'):
                return []
                
            messages = []
            for item in response['items']:
                messages.append({
                    'user': item['authorDetails']['displayName'],
                    'message': item['snippet']['displayMessage'],
                    'timestamp': datetime.strptime(
                        item['snippet']['publishedAt'].split('.')[0] + 'Z',
                        '%Y-%m-%dT%H:%M:%SZ'
                    )
                })
                
            return messages
            
        except Exception as e:
            cprint(f"❌ Error getting API messages: {str(e)}", "red")
            return []
            
    def __del__(self):
        """Clean up resources"""
        if self.scraper:
            self.scraper.close()

class ChatAgent:
    def __init__(self):
        """Initialize the Chat Agent"""
        cprint("\n🤖 Initializing Moon Dev's Chat Agent...", "cyan")
        
        # Create data directories
        self.data_dir = Path(project_root) / "src" / "data" / "chat_agent"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.knowledge_base_path = self.data_dir / "knowledge_base.txt"
        self.chat_log_path = self.data_dir / "chat_history.csv"
        self.config_path = self.data_dir / "config.json"
        
        # Initialize chat memory
        self.chat_memory = []
        
        # Create knowledge base if it doesn't exist
        if not self.knowledge_base_path.exists():
            self._create_knowledge_base()
        
        # Create chat log if it doesn't exist
        if not self.chat_log_path.exists():
            self._create_chat_log()
            
        # Create or load config
        if not self.config_path.exists():
            self._create_config()
        self.config = self._load_config()
        
        # Debug environment variables
        for key in ["OPENAI_KEY", "ANTHROPIC_KEY", "GEMINI_KEY", "GROQ_API_KEY", "DEEPSEEK_KEY", "YOUTUBE_API_KEY"]:
            if os.getenv(key):
                cprint(f"✅ Found {key}", "green")
            else:
                cprint(f"❌ Missing {key}", "red")
        
        # Initialize model using factory
        self.model_factory = model_factory
        self.model = self.model_factory.get_model(MODEL_TYPE, MODEL_NAME)
        
        if not self.model:
            raise ValueError(f"🚨 Could not initialize {MODEL_TYPE} {MODEL_NAME} model! Check API key and model availability.")
        
        self._announce_model()
        
        # Initialize YouTube chat monitor
        youtube_api_key = os.getenv("YOUTUBE_API_KEY")
        if not youtube_api_key:
            raise ValueError("🚨 YOUTUBE_API_KEY not found in environment variables!")
            
        self.youtube_monitor = YouTubeChatMonitor(youtube_api_key)
        
        cprint("🎯 Moon Dev's Chat Agent initialized!", "green")
        
    def _create_config(self):
        """Create initial config file"""
        config = {
            "response_prefix": "🤖 Moon Dev AI: ",
            "ignored_users": ["Nightbot", "StreamElements"],
            "command_prefix": "!",
            "initial_chats": DEFAULT_INITIAL_CHATS  # Add to config
        }
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=4)
        cprint("⚙️ Created initial config file!", "green")
        
    def _load_config(self):
        """Load config from file"""
        with open(self.config_path, 'r') as f:
            return json.load(f)
        
    def _create_knowledge_base(self):
        """Create initial knowledge base file"""
        initial_knowledge = """# 🌙 Moon Dev's Knowledge Base

## About Moon Dev
- Passionate about AI, trading, and coding
- Loves adding emojis to everything
- Streams coding sessions on YouTube
- Built multiple AI trading agents

## Projects
- Focus Agent: AI that monitors focus during streams
- Trading Agents: Various AI-powered trading bots
- Model Factory: Unified interface for multiple AI models

## Preferences
- Favorite Language: Python
- Coding Style: Clean, well-documented, with lots of emojis
- Trading Style: AI-assisted with risk management

## Common Commands
- !focus - Check current focus level
- !trade - Check trading status
- !help - List available commands
"""
        self.knowledge_base_path.write_text(initial_knowledge)
        cprint("📚 Created initial knowledge base!", "green")
        
    def _create_chat_log(self):
        """Create empty chat history CSV"""
        df = pd.DataFrame(columns=['timestamp', 'user', 'question', 'confidence', 'response'])
        df.to_csv(self.chat_log_path, index=False)
        cprint("📝 Created chat history log!", "green")
        
    def _announce_model(self):
        """Announce current model with eye-catching formatting"""
        model_msg = f"🤖 USING MODEL: {MODEL_TYPE.upper()} - {MODEL_NAME} 🤖"
        border = "=" * (len(model_msg) + 4)
        cprint(border, 'white', 'on_blue', attrs=['bold'])
        cprint(f"  {model_msg}  ", 'white', 'on_blue', attrs=['bold'])
        cprint(border, 'white', 'on_blue', attrs=['bold'])
        
    def _load_knowledge_base(self):
        """Load and return the knowledge base content"""
        return self.knowledge_base_path.read_text()
        
    def _log_chat(self, user, question, confidence, response):
        """Log chat interaction to CSV silently"""
        try:
            new_data = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'user': user,
                'question': question,
                'confidence': confidence,
                'response': response
            }
            
            df = pd.read_csv(self.chat_log_path)
            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            df.to_csv(self.chat_log_path, index=False)
            
        except Exception as e:
            cprint(f"❌ Error logging chat: {str(e)}", "red")
            
    def _update_chat_memory(self, message):
        """Update the chat memory with new message"""
        self.chat_memory.append(message)
        if len(self.chat_memory) > CHAT_MEMORY_SIZE:
            self.chat_memory.pop(0)  # Remove oldest message

    def _get_random_lucky_emojis(self, count=3):
        """Get random lucky emojis for 777 responses"""
        return ' '.join(random.sample(LUCKY_EMOJIS, count))

    def _should_skip_response(self, message):
        """Check if message should be skipped for response"""
        # Never skip 777 messages
        if message.strip() == "777":
            return False
        
        # Skip if empty
        if not message.strip():
            return True
        
        # Skip if too short
        if len(message.strip()) < MIN_CHARS_FOR_RESPONSE:
            return True
        
        return False

    def _display_chat(self, user, message, ai_response):
        """Display chat in two-line format with colors"""
        # Clear previous lines
        print("\033[K", end="")  # Clear current line
        
        # Display user message with only username on blue background
        print(f"{random.choice(USER_EMOJIS)} ", end="")
        cprint(user, "white", "on_blue", end="")
        print(f": {message}")
        
        # Only display AI response if we have one
        if ai_response:
            # If it's a clown response, display differently
            if ai_response == CLOWN_SPAM:
                print(f"{random.choice(USER_EMOJIS)} ", end="")
                cprint(user, "white", "on_red", end="")
                print(f" is a {CLOWN_SPAM}")
            # If it's a 777 response, display with cyan background
            elif message.strip() == "777":
                print(f"{random.choice(AI_EMOJIS)} ", end="")
                cprint("Moon Dev AI", "white", "on_green", end="")
                print(": ", end="")
                cprint(ai_response, "white", "on_cyan")
            else:
                print(f"{random.choice(AI_EMOJIS)} ", end="")
                cprint("Moon Dev AI", "white", "on_green", end="")
                print(f": {ai_response}")
        print()  # Add a small space between messages

    def process_question(self, user, question):
        """Process a question and generate a response"""
        try:
            # Skip messages from ignored users
            if user in self.config['ignored_users']:
                return None
                
            # Check for negativity using AI
            negativity_prompt = NEGATIVITY_CHECK_PROMPT.format(message=question)
            negativity_response = self.model.generate_response(
                system_prompt=negativity_prompt,
                user_content=question,
                temperature=0.3,
                max_tokens=10
            )
            try:
                negativity_score = float(negativity_response.content.strip())
                if negativity_score >= NEGATIVITY_THRESHOLD:
                    return CLOWN_SPAM
            except ValueError:
                pass  # If we can't parse the score, continue with message processing
                
            # Special case for "777" - Get AI generated Bible verse
            if question.strip() == "777":
                verse_response = self.model.generate_response(
                    system_prompt=PROMPT_777,
                    user_content="777",
                    temperature=0.9,
                    max_tokens=100
                )
                emojis = self._get_random_lucky_emojis()
                return f"777 {emojis}\n{verse_response.content.strip()}"
                
            # Skip messages that don't need responses
            if self._should_skip_response(question):
                return None
                
            # Load knowledge base and recent chat context - OPTIMIZED
            knowledge_base = self._load_knowledge_base()
            # Only include last 5 messages to reduce context size
            recent_chats = self.chat_memory[-5:]  
            chat_context = ""
            if recent_chats:
                chat_context = "\nRecent messages:\n" + "\n".join([
                    f"{msg['user']}: {msg['message']}" 
                    for msg in recent_chats
                ])
            
            # Format prompt with minimal context
            prompt = f"""You are Moon Dev's Chat AI Agent. Answer questions from YouTube chat.
Keep responses concise, friendly, and include emojis.

Key Info:
- Moon Dev loves AI, trading, and coding
- Streams coding sessions on YouTube
- Built AI trading agents and tools
- Uses Python with clean code and emojis

Question: {question}

IMPORTANT TRANSLATION RULES:
1. If the question is NOT in English:
   - First line: "TRANSLATION: [English translation of their message]"
   - Second line: "CONFIDENCE: X.XX"
   - Third line: "RESPONSE: [Response in their language]"
   - Fourth line: "ENGLISH: [English translation of your response]"

2. If the question is in English:
   - First line: "CONFIDENCE: X.XX"
   - Second line: "RESPONSE: [Your response with emojis]"

Keep responses concise and friendly. If unsure, say "I'll let Moon Dev answer that! 🌙"
"""
            
            # Get response from model with reduced tokens
            response = self.model.generate_response(
                system_prompt=prompt,
                user_content=question,
                temperature=0.7,
                max_tokens=100
            )
            
            # Parse response with translation support
            lines = response.content.strip().split('\n')
            
            # Check if first line is a translation
            if lines[0].startswith('TRANSLATION:'):
                # Handle non-English conversation
                translation = lines[0].split(':', 1)[1].strip()
                confidence = float(lines[1].split(':', 1)[1].strip())
                response_text = lines[2].split(':', 1)[1].strip()
                english = lines[3].split(':', 1)[1].strip()
                
                # Format response with both languages
                if confidence >= CONFIDENCE_THRESHOLD:
                    return f"{response_text}\n\n💭 Translation: {translation}\n{random.choice(AI_EMOJIS)} Moon Dev AI: {english}"
            else:
                # Handle English conversation
                confidence = float(lines[0].split(':', 1)[1].strip())
                response_text = lines[1].split(':', 1)[1].strip()
                
                if confidence >= CONFIDENCE_THRESHOLD:
                    return response_text
                    
            return None
                
        except Exception as e:
            cprint(f"❌ Error processing question: {str(e)}", "red")
            return None

    def run(self):
        """Main loop for monitoring YouTube chat"""
        cprint("\n🎯 Moon Dev's Chat Agent starting...", "cyan", attrs=['bold'])
        print()  # Add a blank line
        
        first_run = True
        initial_chats = self.config.get('initial_chats', DEFAULT_INITIAL_CHATS)
        cprint(f"📝 Will process last {initial_chats} messages on startup", "cyan")
        
        while True:
            try:
                # Use appropriate intervals based on mode
                check_interval = SELENIUM_CHECK_INTERVAL if self.youtube_monitor.using_fallback else CHECK_INTERVAL
                live_check_interval = SELENIUM_LIVE_CHECK_INTERVAL if self.youtube_monitor.using_fallback else LIVE_CHECK_INTERVAL
                
                # Get live chat ID if we don't have one
                if not self.youtube_monitor.live_chat_id:
                    chat_id = self.youtube_monitor.get_live_chat_id(YOUTUBE_CHANNEL_ID)
                    if chat_id:
                        self.youtube_monitor.live_chat_id = chat_id
                        if self.youtube_monitor.using_fallback:
                            cprint("\n✅ Connected to live chat using Selenium fallback!", "green")
                            cprint("💡 Note: Running in fallback mode due to API quota", "yellow")
                            cprint(f"🚀 Using faster {SELENIUM_CHECK_INTERVAL}s check interval", "cyan")
                        else:
                            cprint("✅ Connected to live chat using YouTube API!", "green")
                    else:
                        if self.youtube_monitor.using_fallback:
                            cprint("⏳ Waiting for active live stream (Selenium)...", "yellow")
                        else:
                            cprint("⏳ Waiting for active live stream (API)...", "yellow")
                        time.sleep(live_check_interval)  # Use appropriate interval
                        continue

                # Get messages
                messages = self.youtube_monitor.get_chat_messages()
                
                # On first run, process initial messages
                if first_run and messages:
                    first_run = False
                    cprint(f"\n📥 Processing last {len(messages)} messages...", "cyan")
                    for msg in messages:  # Messages are already in chronological order
                        response = self.process_question(msg['user'], msg['message'])
                        self._display_chat(msg['user'], msg['message'], response)
                    continue

                # Process any new messages
                if messages and not first_run:
                    for msg in messages:
                        response = self.process_question(msg['user'], msg['message'])
                        self._display_chat(msg['user'], msg['message'], response)

                # Wait using appropriate interval
                time.sleep(check_interval)
                
            except KeyboardInterrupt:
                raise
            except Exception as e:
                if "quota" in str(e).lower() and not self.youtube_monitor.using_fallback:
                    cprint("\n🔄 YouTube API quota exceeded!", "yellow")
                    cprint("🚀 Switching to Selenium fallback mode...", "cyan")
                    self.youtube_monitor._init_fallback()
                    continue
                else:
                    cprint(f"❌ Error: {str(e)}", "red")
                time.sleep(check_interval)

if __name__ == "__main__":
    try:
        agent = ChatAgent()
        agent.run()
    except KeyboardInterrupt:
        cprint("\n👋 Chat Agent shutting down gracefully...", "yellow")
    except Exception as e:
        cprint(f"\n❌ Fatal error: {str(e)}", "red")
