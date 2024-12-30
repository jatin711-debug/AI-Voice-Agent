from fastapi import FastAPI, WebSocket, Request, Depends, HTTPException
from .twilio_handler import TwilioHandler
from .websocket_handler import WebSocketClient
from .config import Config
from .logger import setup_logger
from .middleware import RateLimiter, SecurityMiddleware
from .call_recorder import CallRecorder
from .audio_processing import AudioProcessor
import uvicorn

app = FastAPI()
logger = setup_logger(__name__)
config = Config()

twilio_handler = TwilioHandler()
ws_client = WebSocketClient()

rate_limiter = RateLimiter()
security = SecurityMiddleware()
call_recorder = CallRecorder()
audio_processor = AudioProcessor()

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    await rate_limiter.check_rate_limit(request)
    return await call_next(request)

@app.post("/incoming_call")
async def handle_incoming_call(request: Request):
    print("handle_incoming_call")
    """Handle incoming Twilio voice calls"""
    # Verify Twilio signature
    if not await security.verify_twilio_signature(request):
        raise HTTPException(status_code=403, detail="Invalid signature")
    print("twilio_handler.handle_incoming_call()")
    return twilio_handler.handle_incoming_call()

@app.get("/health")
async def health_check():
    """Simple health check endpoint to verify the service is running"""
    return {"status": "healthy", "message": "Service is running"}


@app.websocket("/stream")
async def handle_stream(websocket: WebSocket):
    await websocket.accept()
    
    # Start recording
    recording_file = call_recorder.start_recording(websocket.client.host)
    
    try:
        while True:
            data = await websocket.receive_bytes()
            
            # Save raw audio
            call_recorder.save_audio_chunk(recording_file, data)
            
            # Process audio
            processed_audio = audio_processor.preprocess_audio(data)
            
            # Send to OpenAI
            ai_response = await ws_client.send_audio(processed_audio)
            
            if ai_response and 'text' in ai_response:
                await websocket.send_text(ai_response['text'])
                
    except Exception as e:
        logger.error(f"Error in WebSocket stream: {str(e)}")
    finally:
        await websocket.close()

def run():
    uvicorn.run(
        "src.app:app",
        host=config.HOST,
        port=config.PORT,
        reload=True
    )

if __name__ == "__main__":
    run() 