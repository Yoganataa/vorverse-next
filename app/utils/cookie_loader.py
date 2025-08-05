from pathlib import Path
from typing import Dict, Optional
import logging

class CookieLoader:
    """Utility to parse Netscape-formatted cookie files"""
    
    @staticmethod
    def load_cookies(cookie_file: str) -> Optional[Dict[str, str]]:
        """Load cookies from Netscape format file"""
        cookie_path = Path(cookie_file)
        
        if not cookie_path.exists():
            logging.warning(f"Cookie file not found: {cookie_file}")
            return None
        
        cookies = {}
        
        try:
            with open(cookie_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    
                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse Netscape format: domain, domain_specified, path, secure, expires, name, value
                    parts = line.split('\t')
                    if len(parts) >= 7:
                        name = parts[5]
                        value = parts[6]
                        cookies[name] = value
            
            logging.info(f"Loaded {len(cookies)} cookies from {cookie_file}")
            return cookies
            
        except Exception as e:
            logging.error(f"Error loading cookies from {cookie_file}: {e}")
            return None
    
    @staticmethod
    def cookies_to_string(cookies: Dict[str, str]) -> str:
        """Convert cookies dict to string format"""
        return '; '.join([f"{name}={value}" for name, value in cookies.items()])