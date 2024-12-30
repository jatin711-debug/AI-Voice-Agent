import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Twilio credentials
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
    
    # OpenAI credentials
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # WebSocket configuration
    WEBSOCKET_URL = os.getenv('WEBSOCKET_URL', 'wss://api.openai.com/v1/audio/speech')
    
    # Audio configuration
    SAMPLE_RATE = 16000
    CHANNELS = 1
    
    # Server configuration
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 8000)) 