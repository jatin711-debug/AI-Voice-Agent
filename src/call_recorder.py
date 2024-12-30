from datetime import datetime
import os
from .config import Config
from .logger import setup_logger

logger = setup_logger(__name__)

class CallRecorder:
    def __init__(self):
        self.config = Config()
        self.recordings_dir = "recordings"
        self._ensure_recordings_dir()
        
    def _ensure_recordings_dir(self):
        if not os.path.exists(self.recordings_dir):
            os.makedirs(self.recordings_dir)
    
    def start_recording(self, call_sid: str) -> str:
        """Start recording a call"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.recordings_dir}/{call_sid}_{timestamp}.wav"
        return filename
    
    def save_audio_chunk(self, filename: str, audio_data: bytes):
        """Save an audio chunk to the recording file"""
        try:
            with open(filename, 'ab') as f:
                f.write(audio_data)
        except Exception as e:
            logger.error(f"Error saving audio chunk: {str(e)}") 