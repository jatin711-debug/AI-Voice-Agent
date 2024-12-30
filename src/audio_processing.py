import numpy as np
import soundfile as sf
from io import BytesIO
from .config import Config
from .logger import setup_logger

logger = setup_logger(__name__)

class AudioProcessor:
    def __init__(self):
        self.config = Config()
        
    def preprocess_audio(self, audio_data: bytes) -> bytes:
        """Preprocess audio data from Twilio stream"""
        try:
            # Convert bytes to numpy array
            audio_np = np.frombuffer(audio_data, dtype=np.int16)
            
            # Resample if needed
            if self.config.SAMPLE_RATE != 16000:
                audio_np = self._resample(audio_np, self.config.SAMPLE_RATE, 16000)
            
            # Normalize audio
            audio_np = self._normalize_audio(audio_np)
            
            # Convert back to bytes
            return audio_np.tobytes()
            
        except Exception as e:
            logger.error(f"Error preprocessing audio: {str(e)}")
            raise
    
    def _normalize_audio(self, audio_np: np.ndarray) -> np.ndarray:
        """Normalize audio to [-1, 1] range"""
        return audio_np / np.max(np.abs(audio_np))
    
    def _resample(self, audio_np: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
        """Resample audio to target sample rate"""
        from scipy import signal
        return signal.resample(audio_np, int(len(audio_np) * target_sr / orig_sr))
    
    def save_audio(self, audio_data: bytes, filename: str):
        """Save audio data to file"""
        try:
            with BytesIO(audio_data) as bio:
                audio_np = np.frombuffer(bio.read(), dtype=np.int16)
                sf.write(filename, audio_np, self.config.SAMPLE_RATE)
        except Exception as e:
            logger.error(f"Error saving audio: {str(e)}")
            raise 