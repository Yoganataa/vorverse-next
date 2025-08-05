import re
from typing import Optional, List, Tuple
from urllib.parse import urlparse, parse_qs

class URLParser:
    """Advanced URL parsing and validation for supported platforms"""
    
    # Platform patterns
    PATTERNS = {
        'tiktok': [
            r'(?:https?://)?(?:www\.)?tiktok\.com/@([^/]+)/video/(\d+)',
            r'(?:https?://)?(?:vm\.tiktok\.com|vt\.tiktok\.com)/([A-Za-z0-9]+)',
            r'(?:https?://)?(?:www\.)?tiktok\.com/t/([A-Za-z0-9]+)',
        ],
        'douyin': [
            r'(?:https?://)?(?:www\.)?douyin\.com/video/(\d+)',
            r'(?:https?://)?v\.douyin\.com/([A-Za-z0-9]+)',
        ],
        'instagram': [
            r'(?:https?://)?(?:www\.)?instagram\.com/p/([A-Za-z0-9_-]+)',
            r'(?:https?://)?(?:www\.)?instagram\.com/reel/([A-Za-z0-9_-]+)',
            r'(?:https?://)?(?:www\.)?instagram\.com/tv/([A-Za-z0-9_-]+)',
        ],
        'youtube': [
            r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([A-Za-z0-9_-]+)',
            r'(?:https?://)?youtu\.be/([A-Za-z0-9_-]+)',
            r'(?:https?://)?(?:www\.)?youtube\.com/shorts/([A-Za-z0-9_-]+)',
        ],
        'twitter': [
            r'(?:https?://)?(?:www\.)?twitter\.com/[^/]+/status/(\d+)',
            r'(?:https?://)?(?:www\.)?x\.com/[^/]+/status/(\d+)',
        ],
        'facebook': [
            r'(?:https?://)?(?:www\.)?facebook\.com/.+/videos/(\d+)',
            r'(?:https?://)?(?:www\.)?fb\.watch/([A-Za-z0-9_-]+)',
        ]
    }
    
    @classmethod
    def detect_platform(cls, url: str) -> Optional[str]:
        """Detect platform from URL"""
        url = url.strip()
        
        for platform, patterns in cls.PATTERNS.items():
            for pattern in patterns:
                if re.match(pattern, url, re.IGNORECASE):
                    return platform
        
        return None
    
    @classmethod
    def extract_urls(cls, text: str) -> List[Tuple[str, str]]:
        """Extract all supported URLs from text with their platforms"""
        urls = []
        
        # Find all URLs in text
        url_pattern = r'https?://[^\s]+'
        found_urls = re.findall(url_pattern, text)
        
        for url in found_urls:
            platform = cls.detect_platform(url)
            if platform:
                urls.append((url, platform))
        
        return urls
    
    @classmethod
    def is_supported_url(cls, url: str) -> bool:
        """Check if URL is supported"""
        return cls.detect_platform(url) is not None
    
    @classmethod
    def normalize_url(cls, url: str) -> str:
        """Normalize URL for processing"""
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url
    
    @classmethod
    def extract_instagram_shortcode(cls, url: str) -> Optional[str]:
        """Extract Instagram shortcode from URL"""
        patterns = [
            r'instagram\.com/p/([A-Za-z0-9_-]+)',
            r'instagram\.com/reel/([A-Za-z0-9_-]+)',
            r'instagram\.com/tv/([A-Za-z0-9_-]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None