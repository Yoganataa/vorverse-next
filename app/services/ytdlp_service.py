from .base_downloader import BaseDownloader
import yt_dlp
from pathlib import Path
from typing import Dict, Any, List
import yaml

class YTDLPService(BaseDownloader):
    """Generic downloader service using yt-dlp for all other platforms"""
    
    def __init__(self, config_obj):
        super().__init__(config_obj)
        self.platform_configs = self._load_platform_configs()
    
    def _load_platform_configs(self) -> Dict[str, Any]:
        """Load platform-specific configurations from platforms.yml"""
        try:
            config_path = Path("./data/platforms.yml")
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
        except Exception as e:
            self.logger.warning(f"Failed to load platforms.yml: {e}")
        
        # Default configuration
        return {
            'youtube': {
                'format': 'best[height<=720]',
                'writesubtitles': False,
                'writeautomaticsub': False
            },
            'twitter': {
                'format': 'best',
                'writeinfojson': True
            },
            'facebook': {
                'format': 'best',
                'writeinfojson': True
            }
        }
    
    def _get_ytdlp_options(self, platform: str, output_path: str) -> Dict[str, Any]:
        """Get yt-dlp options for specific platform"""
        
        platform_config = self.platform_configs.get(platform, {})
        
        # Base options
        options = {
            'outtmpl': str(Path(output_path) / '%(title)s.%(ext)s'),
            'format': platform_config.get('format', self.config.YTDLP_FORMAT),
            'noplaylist': True,
            'extractflat': self.config.YTDLP_EXTRACT_FLAT,
            'writethumbnail': self.config.YTDLP_WRITE_THUMBNAIL,
            'writeinfojson': self.config.YTDLP_WRITE_INFO_JSON,
            'writedescription': self.config.YTDLP_WRITE_DESCRIPTION,
            'no_warnings': False,
            'ignoreerrors': False,
        }
        
        # Merge platform-specific options
        options.update(platform_config)
        
        return options
    
    async def download(self, url: str, output_path: str, platform: str = None) -> Dict[str, Any]:
        """Download media using yt-dlp"""
        
        try:
            # Detect platform if not provided
            if not platform:
                from ..utils.url_parser import URLParser
                platform = URLParser.detect_platform(url) or 'generic'
            
            # Get yt-dlp options
            ydl_opts = self._get_ytdlp_options(platform, output_path)
            
            downloaded_files = []
            metadata = {}
            
            def progress_hook(d):
                if d['status'] == 'finished':
                    downloaded_files.append(d['filename'])
            
            ydl_opts['progress_hooks'] = [progress_hook]
            
            # Download using yt-dlp
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract info first
                info = ydl.extract_info(url, download=False)
                metadata = {
                    'title': info.get('title', ''),
                    'description': info.get('description', ''),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', ''),
                    'upload_date': info.get('upload_date', ''),
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0),
                    'webpage_url': info.get('webpage_url', url)
                }
                
                # Download
                ydl.download([url])
            
            return {
                'success': True,
                'files': downloaded_files,
                'metadata': metadata,
                'platform': platform
            }
            
        except Exception as e:
            self.logger.error(f"yt-dlp download failed for {url}: {e}")
            return {
                'success': False,
                'error': str(e),
                'files': [],
                'platform': platform or 'unknown'
            }