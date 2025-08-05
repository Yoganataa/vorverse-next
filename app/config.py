import os
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

class Config:
    """Centralized configuration management loading all parameters from .env"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Bot Configuration
        self.BOT_TOKEN = os.getenv("BOT_TOKEN")
        self.API_ID = int(os.getenv("API_ID", "0"))
        self.API_HASH = os.getenv("API_HASH")
        
        # Database Configuration
        self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/bot_database.db")
        
        # Download Configuration
        self.DOWNLOAD_PATH = os.getenv("DOWNLOAD_PATH", "./downloads")
        self.MAX_CONCURRENT_DOWNLOADS = int(os.getenv("MAX_CONCURRENT_DOWNLOADS", "5"))
        self.MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "500"))
        self.CLEANUP_DELAY_HOURS = int(os.getenv("CLEANUP_DELAY_HOURS", "24"))
        
        # TikTok Configuration - Complete JoeanAmier/TikTokDownloader Parameters
        self.TIKTOK_COOKIE_FILE = os.getenv("TIKTOK_COOKIE_FILE", "./data/cookies/tiktok.txt")
        self.TIKTOK_ROOT = os.getenv("TIKTOK_ROOT", "./downloads/tiktok")
        self.TIKTOK_FOLDER_NAME = os.getenv("TIKTOK_FOLDER_NAME", "TikTok")
        self.TIKTOK_NAME_FORMAT = os.getenv("TIKTOK_NAME_FORMAT", "{create}_{desc}_{id}")
        self.TIKTOK_DATE_FORMAT = os.getenv("TIKTOK_DATE_FORMAT", "%Y-%m-%d %H.%M.%S")
        self.TIKTOK_SPLIT = os.getenv("TIKTOK_SPLIT", "-")
        self.TIKTOK_FOLDER_MODE = self._parse_bool("TIKTOK_FOLDER_MODE", False)
        self.TIKTOK_MUSIC = self._parse_bool("TIKTOK_MUSIC", False)
        self.TIKTOK_STORAGE_FORMAT = os.getenv("TIKTOK_STORAGE_FORMAT", "")
        self.TIKTOK_COOKIE_FORMAT = os.getenv("TIKTOK_COOKIE_FORMAT", "")
        self.TIKTOK_DYNAMIC_COVER = self._parse_bool("TIKTOK_DYNAMIC_COVER", False)
        self.TIKTOK_ORIGINAL_COVER = self._parse_bool("TIKTOK_ORIGINAL_COVER", False)
        self.TIKTOK_PROXIES = self._parse_json("TIKTOK_PROXIES", {})
        self.TIKTOK_DOWNLOAD = self._parse_bool("TIKTOK_DOWNLOAD", True)
        self.TIKTOK_MAX_SIZE = int(os.getenv("TIKTOK_MAX_SIZE", "104857600"))  # 100MB
        self.TIKTOK_CHUNK = int(os.getenv("TIKTOK_CHUNK", "1048576"))  # 1MB
        self.TIKTOK_MAX_RETRY = int(os.getenv("TIKTOK_MAX_RETRY", "5"))
        self.TIKTOK_RECORD_DATA = self._parse_bool("TIKTOK_RECORD_DATA", True)
        self.TIKTOK_RECORD_FORMAT = os.getenv("TIKTOK_RECORD_FORMAT", "")
        self.TIKTOK_OWNER_URL = os.getenv("TIKTOK_OWNER_URL", "https://github.com/JoeanAmier/TikTokDownloader")
        self.TIKTOK_REPOSITORY_URL = os.getenv("TIKTOK_REPOSITORY_URL", "https://github.com/JoeanAmier/TikTokDownloader")
        self.TIKTOK_COLOUR = self._parse_bool("TIKTOK_COLOUR", True)
        self.TIKTOK_LANGUAGE = os.getenv("TIKTOK_LANGUAGE", "zh")
        
        # Advanced TikTok Parameters - Direct from JoeanAmier settings
        self.TIKTOK_PROJECT_ROOT = os.getenv("TIKTOK_PROJECT_ROOT", "")
        self.TIKTOK_PROJECT_NAME = os.getenv("TIKTOK_PROJECT_NAME", "")
        self.TIKTOK_TIME_OUT = int(os.getenv("TIKTOK_TIME_OUT", "10"))
        self.TIKTOK_MAX_WORKERS = int(os.getenv("TIKTOK_MAX_WORKERS", "4"))
        self.TIKTOK_LOG_LEVEL = os.getenv("TIKTOK_LOG_LEVEL", "INFO")
        self.TIKTOK_LOG_PATH = os.getenv("TIKTOK_LOG_PATH", "./logs/tiktok.log")
        self.TIKTOK_SINGLE_FILE = self._parse_bool("TIKTOK_SINGLE_FILE", False)
        self.TIKTOK_PROGRESS = self._parse_bool("TIKTOK_PROGRESS", True)
        self.TIKTOK_HEADERS = self._parse_json("TIKTOK_HEADERS", {})
        self.TIKTOK_PARAMS = self._parse_json("TIKTOK_PARAMS", {})
        
        # Complex TikTok configurations (JSON strings from .env)
        self.TIKTOK_BROWSER_INFO = self._parse_json("TIKTOK_BROWSER_INFO", {
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"'
            }
        })
        
        # Instagram Configuration - Complete instaloader parameters
        self.INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME", "")
        self.INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD", "")
        self.INSTAGRAM_SESSION_FILE = os.getenv("INSTAGRAM_SESSION_FILE", "./data/instagram_session")
        self.INSTAGRAM_DOWNLOAD_VIDEOS = self._parse_bool("INSTAGRAM_DOWNLOAD_VIDEOS", True)
        self.INSTAGRAM_DOWNLOAD_VIDEO_THUMBNAILS = self._parse_bool("INSTAGRAM_DOWNLOAD_VIDEO_THUMBNAILS", False)
        self.INSTAGRAM_DOWNLOAD_GEOTAGS = self._parse_bool("INSTAGRAM_DOWNLOAD_GEOTAGS", False)
        self.INSTAGRAM_DOWNLOAD_COMMENTS = self._parse_bool("INSTAGRAM_DOWNLOAD_COMMENTS", False)
        self.INSTAGRAM_SAVE_METADATA = self._parse_bool("INSTAGRAM_SAVE_METADATA", True)
        self.INSTAGRAM_COMPRESS_JSON = self._parse_bool("INSTAGRAM_COMPRESS_JSON", False)
        self.INSTAGRAM_DIRNAME_PATTERN = os.getenv("INSTAGRAM_DIRNAME_PATTERN", "{profile}")
        self.INSTAGRAM_FILENAME_PATTERN = os.getenv("INSTAGRAM_FILENAME_PATTERN", "{date_utc}_UTC")
        self.INSTAGRAM_TITLE_PATTERN = os.getenv("INSTAGRAM_TITLE_PATTERN", "{profile} - {date_utc}_UTC")
        self.INSTAGRAM_MAX_CONNECTION_ATTEMPTS = int(os.getenv("INSTAGRAM_MAX_CONNECTION_ATTEMPTS", "3"))
        self.INSTAGRAM_REQUEST_TIMEOUT = float(os.getenv("INSTAGRAM_REQUEST_TIMEOUT", "300.0"))
        self.INSTAGRAM_RATE_CONTROLLER = os.getenv("INSTAGRAM_RATE_CONTROLLER", "default")
        self.INSTAGRAM_RESUME_PREFIX = os.getenv("INSTAGRAM_RESUME_PREFIX", "iterator")
        self.INSTAGRAM_CHECK_RESUME_BTIME = self._parse_bool("INSTAGRAM_CHECK_RESUME_BTIME", True)
        self.INSTAGRAM_SLIDE = self._parse_bool("INSTAGRAM_SLIDE", True)
        self.INSTAGRAM_FAST_UPDATE = self._parse_bool("INSTAGRAM_FAST_UPDATE", False)
        self.INSTAGRAM_IPHONE_SUPPORT = self._parse_bool("INSTAGRAM_IPHONE_SUPPORT", True)
        self.INSTAGRAM_SANITIZE_PATHS = self._parse_bool("INSTAGRAM_SANITIZE_PATHS", True)
        
        # YT-DLP Configuration
        self.YTDLP_FORMAT = os.getenv("YTDLP_FORMAT", "best[height<=720]")
        self.YTDLP_EXTRACT_FLAT = self._parse_bool("YTDLP_EXTRACT_FLAT", False)
        self.YTDLP_WRITE_DESCRIPTION = self._parse_bool("YTDLP_WRITE_DESCRIPTION", False)
        self.YTDLP_WRITE_INFO_JSON = self._parse_bool("YTDLP_WRITE_INFO_JSON", False)
        self.YTDLP_WRITE_THUMBNAIL = self._parse_bool("YTDLP_WRITE_THUMBNAIL", False)
        self.YTDLP_WRITE_SUBTITLES = self._parse_bool("YTDLP_WRITE_SUBTITLES", False)
        self.YTDLP_WRITE_AUTO_SUBTITLES = self._parse_bool("YTDLP_WRITE_AUTO_SUBTITLES", False)
        self.YTDLP_NO_PLAYLIST = self._parse_bool("YTDLP_NO_PLAYLIST", True)
        self.YTDLP_IGNORE_ERRORS = self._parse_bool("YTDLP_IGNORE_ERRORS", False)
        self.YTDLP_CONCURRENT_FRAGMENT_DOWNLOADS = int(os.getenv("YTDLP_CONCURRENT_FRAGMENT_DOWNLOADS", "1"))
        
        # Admin Configuration
        self.ADMIN_IDS = self._parse_list("ADMIN_IDS", [])
        
        # Logging Configuration
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_FILE = os.getenv("LOG_FILE", "./logs/bot.log")
        self.LOG_MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", "10485760"))  # 10MB
        self.LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", "5"))
        
        # Validate required configurations
        self._validate_config()
        
        self.logger.info("Configuration loaded successfully")
    
    def _parse_bool(self, key: str, default: bool = False) -> bool:
        """Parse boolean value from environment variable"""
        value = os.getenv(key, "").lower()
        if value in ("true", "1", "yes", "on"):
            return True
        elif value in ("false", "0", "no", "off"):
            return False
        return default
    
    def _parse_json(self, key: str, default: Dict[str, Any] = None) -> Dict[str, Any]:
        """Parse JSON string from environment variable"""
        if default is None:
            default = {}
        
        try:
            value = os.getenv(key)
            if value:
                parsed = json.loads(value)
                self.logger.debug(f"Parsed JSON for {key}: {type(parsed)}")
                return parsed
            return default
        except json.JSONDecodeError as e:
            self.logger.warning(f"Invalid JSON for {key}: {e}")
            return default
        except Exception as e:
            self.logger.error(f"Error parsing {key}: {e}")
            return default
    
    def _parse_list(self, key: str, default: List[str] = None) -> List[str]:
        """Parse comma-separated list from environment variable"""
        if default is None:
            default = []
        
        value = os.getenv(key)
        if value:
            return [item.strip() for item in value.split(",") if item.strip()]
        return default
    
    def get_tiktok_settings_dict(self) -> Dict[str, Any]:
        """Get complete TikTok settings dictionary for JoeanAmier bridge"""
        return {
            "root": self.TIKTOK_ROOT,
            "folder_name": self.TIKTOK_FOLDER_NAME,
            "name_format": self.TIKTOK_NAME_FORMAT,
            "date_format": self.TIKTOK_DATE_FORMAT,
            "split": self.TIKTOK_SPLIT,
            "folder_mode": self.TIKTOK_FOLDER_MODE,
            "music": self.TIKTOK_MUSIC,
            "storage_format": self.TIKTOK_STORAGE_FORMAT,
            "cookie_format": self.TIKTOK_COOKIE_FORMAT,
            "dynamic_cover": self.TIKTOK_DYNAMIC_COVER,
            "original_cover": self.TIKTOK_ORIGINAL_COVER,
            "proxies": self.TIKTOK_PROXIES,
            "download": self.TIKTOK_DOWNLOAD,
            "max_size": self.TIKTOK_MAX_SIZE,
            "chunk": self.TIKTOK_CHUNK,
            "max_retry": self.TIKTOK_MAX_RETRY,
            "record_data": self.TIKTOK_RECORD_DATA,
            "record_format": self.TIKTOK_RECORD_FORMAT,
            "owner_url": self.TIKTOK_OWNER_URL,
            "repository_url": self.TIKTOK_REPOSITORY_URL,
            "colour": self.TIKTOK_COLOUR,
            "language": self.TIKTOK_LANGUAGE,
            "browser_info": self.TIKTOK_BROWSER_INFO,
            "project_root": self.TIKTOK_PROJECT_ROOT,
            "project_name": self.TIKTOK_PROJECT_NAME,
            "time_out": self.TIKTOK_TIME_OUT,
            "max_workers": self.TIKTOK_MAX_WORKERS,
            "log_level": self.TIKTOK_LOG_LEVEL,
            "log_path": self.TIKTOK_LOG_PATH,
            "single_file": self.TIKTOK_SINGLE_FILE,
            "progress": self.TIKTOK_PROGRESS,
            "headers": self.TIKTOK_HEADERS,
            "params": self.TIKTOK_PARAMS
        }
    
    def _validate_config(self):
        """Validate required configuration"""
        required_fields = {
            "BOT_TOKEN": self.BOT_TOKEN,
            "API_ID": self.API_ID,
            "API_HASH": self.API_HASH
        }
        
        missing_fields = [field for field, value in required_fields.items() if not value]
        
        if missing_fields:
            raise ValueError(f"Missing required configuration: {', '.join(missing_fields)}")
        
        # Validate paths
        Path(self.DOWNLOAD_PATH).mkdir(parents=True, exist_ok=True)
        Path(self.LOG_FILE).parent.mkdir(parents=True, exist_ok=True)
        
        # Validate TikTok cookie file path
        if self.TIKTOK_COOKIE_FILE:
            cookie_path = Path(self.TIKTOK_COOKIE_FILE)
            cookie_path.parent.mkdir(parents=True, exist_ok=True)

# Global config instance
config = Config()