from twilio.twiml.voice_response import VoiceResponse, Start
from twilio.rest import Client
from .config import Config
from .logger import setup_logger

logger = setup_logger(__name__)

class TwilioHandler:
    def __init__(self):
        self.config = Config()
        self.client = Client(
            self.config.TWILIO_ACCOUNT_SID,
            self.config.TWILIO_AUTH_TOKEN
        )

    def handle_incoming_call(self):
        response = VoiceResponse()
        
        # Start a stream
        start = Start()
        start.stream(
            url=f'wss://{self.config.HOST}:{self.config.PORT}/stream'
        )
        response.append(start)
        
        # Add initial greeting
        response.say(
            'Hello, I am your AI assistant. How can I help you today?',
            voice='neural'
        )
        
        return str(response)

    def handle_stream(self, stream_sid, audio_data):
        """Handle incoming audio stream from Twilio"""
        return audio_data

    def send_audio_response(self, call_sid, audio_response):
        """Send AI-generated audio response back to the call"""
        try:
            self.client.calls(call_sid).update(
                twiml=f'<Response><Say voice="neural">{audio_response}</Say></Response>'
            )
        except Exception as e:
            logger.error(f"Error sending audio response: {str(e)}") 