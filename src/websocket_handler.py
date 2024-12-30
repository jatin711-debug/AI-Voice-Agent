import asyncio
import json
import websockets
from .config import Config
from .logger import setup_logger
import backoff

logger = setup_logger(__name__)

class WebSocketClient:
    def __init__(self):
        self.config = Config()
        self.ws = None
        self.is_connected = False
        self.max_retries = 3
        self.retry_delay = 1  # seconds

    @backoff.on_exception(
        backoff.expo,
        (websockets.WebSocketException, ConnectionError),
        max_tries=3
    )
    async def connect(self):
        try:
            headers = {
                "Authorization": f"Bearer {self.config.OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            
            self.ws = await websockets.connect(
                self.config.WEBSOCKET_URL,
                extra_headers=headers
            )
            self.is_connected = True
            logger.info("Successfully connected to OpenAI WebSocket")
            
        except Exception as e:
            logger.error(f"Failed to connect to WebSocket: {str(e)}")
            self.is_connected = False
            raise

    @backoff.on_exception(
        backoff.expo,
        Exception,
        max_tries=3
    )
    async def send_audio(self, audio_data):
        if not self.is_connected:
            await self.connect()
            
        try:
            await self.ws.send(audio_data)
            response = await self.ws.recv()
            return json.loads(response)
            
        except Exception as e:
            logger.error(f"Error in WebSocket communication: {str(e)}")
            self.is_connected = False
            raise

    async def close(self):
        if self.ws:
            await self.ws.close()
            self.is_connected = False 