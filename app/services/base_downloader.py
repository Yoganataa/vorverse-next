import asyncio
import aiohttp
import aiofiles
from pathlib import Path
from typing import Optional, Dict, Any
import logging
from abc import ABC, abstractmethod

class BaseDownloader(ABC):
    """Abstract base class for downloader services"""
    
    def __init__(self, config_obj):
        self.config = config_obj
        self.logger = logging.getLogger(self.__class__.__name__)
        self.session = None
    
    async def __aenter__(self):
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=10)
        timeout = aiohttp.ClientTimeout(total=300, connect=30)
        self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    @abstractmethod
    async def download(self, url: str, output_path: str) -> Dict[str, Any]:
        """Download media from URL"""
        pass
    
    async def download_file_advanced(self, url: str, filepath: str, 
                                   headers: Dict[str, str] = None) -> bool:
        """Advanced file download with resume capability and atomic operations"""
        filepath = Path(filepath)
        temp_filepath = filepath.with_suffix(filepath.suffix + '.cache')
        
        # Ensure directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if partial file exists
        resume_byte_pos = 0
        if temp_filepath.exists():
            resume_byte_pos = temp_filepath.stat().st_size
        
        # Prepare headers
        request_headers = headers or {}
        if resume_byte_pos > 0:
            request_headers['Range'] = f'bytes={resume_byte_pos}-'
        
        try:
            async with self.session.get(url, headers=request_headers) as response:
                # Handle resume
                if resume_byte_pos > 0 and response.status == 206:
                    mode = 'ab'
                elif response.status == 200:
                    mode = 'wb'
                    resume_byte_pos = 0  # Reset if full download
                else:
                    response.raise_for_status()
                    return False
                
                # Verify content type
                content_type = response.headers.get('content-type', '')
                if not self._is_valid_media_type(content_type):
                    self.logger.warning(f"Unexpected content type: {content_type}")
                
                # Download with atomic write
                async with aiofiles.open(temp_filepath, mode) as f:
                    downloaded = resume_byte_pos
                    
                    async for chunk in response.content.iter_chunked(8192):
                        await f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Check file size limit
                        if downloaded > self.config.MAX_FILE_SIZE_MB * 1024 * 1024:
                            raise ValueError(f"File too large: {downloaded} bytes")
                
                # Atomic move to final location
                temp_filepath.rename(filepath)
                self.logger.info(f"Downloaded: {filepath} ({downloaded} bytes)")
                return True
                
        except Exception as e:
            self.logger.error(f"Download failed for {url}: {e}")
            # Cleanup on failure
            if temp_filepath.exists():
                temp_filepath.unlink()
            return False
    
    def _is_valid_media_type(self, content_type: str) -> bool:
        """Check if content type is valid media"""
        valid_types = [
            'video/', 'image/', 'audio/',
            'application/octet-stream',
            'application/x-mpegURL'
        ]
        return any(content_type.startswith(vtype) for vtype in valid_types)