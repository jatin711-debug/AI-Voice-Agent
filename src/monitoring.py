from datetime import datetime
import json
from typing import Dict, List
from .logger import setup_logger

logger = setup_logger(__name__)

class CallAnalytics:
    def __init__(self):
        self.calls: Dict[str, Dict] = {}
        
    def start_call(self, call_sid: str):
        self.calls[call_sid] = {
            'start_time': datetime.now(),
            'duration': 0,
            'audio_chunks': 0,
            'ai_responses': 0,
            'errors': []
        }
    
    def end_call(self, call_sid: str):
        if call_sid in self.calls:
            self.calls[call_sid]['duration'] = (
                datetime.now() - self.calls[call_sid]['start_time']
            ).total_seconds()
    
    def log_error(self, call_sid: str, error: str):
        if call_sid in self.calls:
            self.calls[call_sid]['errors'].append({
                'timestamp': datetime.now(),
                'error': str(error)
            })
    
    def get_call_stats(self, call_sid: str) -> Dict:
        return self.calls.get(call_sid, {})
    
    def save_analytics(self, filename: str):
        with open(filename, 'w') as f:
            json.dump(self.calls, f, default=str) 