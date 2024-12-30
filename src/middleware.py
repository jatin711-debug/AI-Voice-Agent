from fastapi import Request, HTTPException
from typing import Callable, Dict
import time
import hmac
import hashlib
from .config import Config
from .logger import setup_logger

logger = setup_logger(__name__)

class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = {}
    
    async def check_rate_limit(self, request: Request):
        client_ip = request.client.host
        current_time = time.time()
        
        # Clean old requests
        if client_ip in self.requests:
            self.requests[client_ip] = [
                req_time for req_time in self.requests[client_ip]
                if current_time - req_time < 60
            ]
        else:
            self.requests[client_ip] = []
        
        # Check rate limit
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
        self.requests[client_ip].append(current_time)

class SecurityMiddleware:
    def __init__(self):
        self.config = Config()
    
    async def verify_twilio_signature(self, request: Request) -> bool:
        """Verify that the request came from Twilio"""
        twilio_signature = request.headers.get('X-Twilio-Signature')
        if not twilio_signature:
            return False
        
        # Build the validation string
        validation_string = str(request.url)
        print(f"validation_string: {validation_string}")
        if request.method == 'POST':
            form_data = await request.form()
            validation_string += ''.join(
                f"{k}{form_data[k]}" 
                for k in sorted(form_data.keys())
            )
        
        # Generate signature
        expected_signature = hmac.new(
            self.config.TWILIO_AUTH_TOKEN.encode(),
            validation_string.encode(),
            hashlib.sha1
        ).hexdigest()
        print(f"expected_signature: {expected_signature}")
        print(f"twilio_signature: {twilio_signature}")
        return hmac.compare_digest(twilio_signature, expected_signature) 