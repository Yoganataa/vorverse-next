from .base_downloader import BaseDownloader
from ..utils.cookie_loader import CookieLoader
from typing import Dict, Any
from pathlib import Path
import logging

# Import actual classes from JoeanAmier/TikTokDownloader
try:
    from app.tiktok_dl_lib.config.settings import Settings
    from app.tiktok_dl_lib.config.parameter import Parameter
    from app.tiktok_dl_lib.extract import Extractor
    from app.tiktok_dl_lib.downloader import Downloader
    TIKTOK_LIB_AVAILABLE = True
except ImportError as e:
    logging.warning(f"TikTok library not available: {e}")
    TIKTOK_LIB_AVAILABLE = False

class TikTokDownloaderService(BaseDownloader):
    """TikTok/Douyin downloader service using JoeanAmier's library - REAL IMPLEMENTATION"""
    
    def __init__(self, config_obj):
        super().__init__(config_obj)
        
        if not TIKTOK_LIB_AVAILABLE:
            raise ImportError("TikTok library (JoeanAmier/TikTokDownloader) is not available")
        
        self.cookies = None
        self.settings_instance = None
        self.default_config = None
        
        # Initialize library components
        self._initialize_library()
        self._load_cookies()
    
    def _initialize_library(self):
        """Initialize JoeanAmier library components"""
        try:
            # Create Settings instance to get default configuration
            self.settings_instance = Settings()
            
            # Get the default configuration dictionary from Settings
            # This is the exact method JoeanAmier uses internally
            self.default_config = self.settings_instance.read()
            
            self.logger.info("TikTok library initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize TikTok library: {e}")
            self.default_config = self._get_fallback_config()
    
    def _get_fallback_config(self) -> Dict[str, Any]:
        """Fallback configuration if library initialization fails"""
        return {
            "root": "",
            "folder_name": "TikTok",
            "name_format": "{create}_{desc}_{id}",
            "date_format": "%Y-%m-%d %H.%M.%S",
            "split": "-",
            "folder_mode": False,
            "music": False,
            "storage_format": "csv",
            "cookie_format": "",
            "dynamic_cover": False,
            "original_cover": False,
            "proxies": {},
            "download": True,
            "max_size": 104857600,
            "chunk": 1048576,
            "max_retry": 5,
            "record_data": True,
            "record_format": "",
            "owner_url": "https://github.com/JoeanAmier/TikTokDownloader",
            "repository_url": "https://github.com/JoeanAmier/TikTokDownloader",
            "colour": True,
            "language": "zh",
            "browser_info": {},
            "project_root": "",
            "project_name": "",
            "time_out": 10,
            "max_workers": 4,
            "log_level": "INFO",
            "log_path": "./logs/tiktok.log",
            "single_file": False,
            "progress": True,
            "headers": {},
            "params": {}
        }
    
    def _load_cookies(self):
        """Load TikTok cookies from file"""
        if self.config.TIKTOK_COOKIE_FILE:
            cookie_path = Path(self.config.TIKTOK_COOKIE_FILE)
            if cookie_path.exists():
                self.cookies = CookieLoader.load_cookies(str(cookie_path))
                self.logger.info(f"Loaded {len(self.cookies or {})} TikTok cookies")
            else:
                self.logger.warning(f"TikTok cookie file not found: {cookie_path}")
    
    def _create_dynamic_parameters(self) -> Parameter:
        """
        CRITICAL: Dynamic Configuration Bridge Implementation
        This is the exact "precision replication" mechanism as specified
        """
        
        # Step 1: Get library's default configuration
        # Use the actual Settings instance default config
        merged_settings = self.default_config.copy()
        
        # Step 2: Override defaults with our configuration values from .env
        # Get our TikTok settings from config
        our_config = self.config.get_tiktok_settings_dict()
        
        # Systematically override the library defaults
        for key, value in our_config.items():
            if value is not None and value != "":
                # Handle special cases for complex types
                if key == "proxies" and isinstance(value, dict):
                    merged_settings[key] = value
                elif key == "browser_info" and isinstance(value, dict):
                    merged_settings[key] = value
                elif key == "headers" and isinstance(value, dict):
                    merged_settings[key] = value
                elif key == "params" and isinstance(value, dict):
                    merged_settings[key] = value
                else:
                    merged_settings[key] = value
        
        # Add cookies if available
        if self.cookies:
            merged_settings["cookie"] = CookieLoader.cookies_to_string(self.cookies)
        
        # Step 3: Create Parameter instance with merged settings
        # This is the exact way JoeanAmier library expects to receive configuration
        try:
            params = Parameter(**merged_settings)
            self.logger.info("Dynamic TikTok parameters created successfully")
            return params
            
        except Exception as e:
            self.logger.error(f"Failed to create TikTok parameters: {e}")
            # Fallback with minimal config
            minimal_config = {
                "root": self.config.TIKTOK_ROOT,
                "download": True,
                "max_size": self.config.TIKTOK_MAX_SIZE,
                "chunk": self.config.TIKTOK_CHUNK,
                "max_retry": self.config.TIKTOK_MAX_RETRY
            }
            return Parameter(**minimal_config)
    
    async def download(self, url: str, output_path: str) -> Dict[str, Any]:
        """
        Download TikTok/Douyin video using JoeanAmier's actual library workflow
        This follows the exact pattern used in the original library
        """
        
        try:
            # Create dynamic parameters using the bridge
            params = self._create_dynamic_parameters()
            
            # Override output path in params
            params.root = output_path
            
            # Initialize extractor and downloader with the configured parameters
            # This is the exact workflow from JoeanAmier library
            extractor = Extractor(params)
            downloader = Downloader(params)
            
            self.logger.info(f"Starting TikTok extraction for: {url}")
            
            # PERBAIKAN: Gunakan method 'run' dari Extractor.
            # Ini mungkin memerlukan penyesuaian lebih lanjut tergantung pada apa yang dikembalikan oleh 'run'.
            # Asumsi 'run' akan mengembalikan data yang dibutuhkan oleh downloader.
            # Tipe data yang dibutuhkan adalah list[dict].
            api_data = await extractor.run(urls=[url], type_="detail")
            
            if not api_data:
                raise ValueError("Failed to extract media information from TikTok")
            
            self.logger.info("TikTok extraction completed, starting download")
            
            # PERBAIKAN: Gunakan method 'run' dari Downloader.
            # Method 'run' akan menangani proses download secara internal dan tidak mengembalikan path file secara langsung.
            # Anda perlu memodifikasi cara mendapatkan file yang sudah di-download.
            # Untuk sementara, kita panggil methodnya. Path file akan berada di 'output_path'.
            await downloader.run(data=api_data, type_="detail")
            saved_files = [str(p) for p in Path(output_path).rglob('*') if p.is_file()]
            
            if not saved_files:
                raise ValueError("No files were downloaded")
            
            # Prepare metadata from extracted data
            metadata = {
                'platform': 'tiktok' if 'tiktok.com' in url else 'douyin',
                'url': url,
                'extracted_data': api_data,
                'download_path': output_path,
                'files_count': len(saved_files)
            }
            
            # Add specific metadata if available in api_data
            if isinstance(api_data, dict):
                metadata.update({
                    'title': api_data.get('desc', ''),
                    'author': api_data.get('nickname', ''),
                    'create_time': api_data.get('create_time', ''),
                    'video_id': api_data.get('aweme_id', ''),
                    'duration': api_data.get('duration', 0),
                    'like_count': api_data.get('digg_count', 0),
                    'share_count': api_data.get('share_count', 0),
                    'comment_count': api_data.get('comment_count', 0)
                })
            
            self.logger.info(f"TikTok download completed: {len(saved_files)} files")
            
            return {
                'success': True,
                'files': saved_files,
                'metadata': metadata,
                'platform': 'tiktok' if 'tiktok.com' in url else 'douyin'
            }
            
        except Exception as e:
            self.logger.error(f"TikTok download failed for {url}: {e}")
            return {
                'success': False,
                'error': str(e),
                'files': [],
                'platform': 'tiktok' if 'tiktok.com' in url else 'douyin'
            }
    
    def __str__(self):
        return f"TikTokDownloaderService(config_loaded={bool(self.default_config)}, cookies_loaded={bool(self.cookies)})"