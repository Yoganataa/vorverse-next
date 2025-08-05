from .base_downloader import BaseDownloader
from ..utils.url_parser import URLParser
import instaloader
from pathlib import Path
from typing import Dict, Any, List, Optional
import tempfile
import shutil
import logging

class InstagramDownloaderService(BaseDownloader):
    """Instagram downloader service using instaloader with complete configuration"""
    
    def __init__(self, config_obj):
        super().__init__(config_obj)
        self.loader = None
        self.context = None
        self._initialize_instaloader()
    
    def _initialize_instaloader(self):
        """Initialize instaloader with complete configuration from config"""
        
        try:
            # Create instaloader with all advanced parameters from config
            self.loader = instaloader.Instaloader(
                # Download options
                download_videos=self.config.INSTAGRAM_DOWNLOAD_VIDEOS,
                download_video_thumbnails=self.config.INSTAGRAM_DOWNLOAD_VIDEO_THUMBNAILS,
                download_geotags=self.config.INSTAGRAM_DOWNLOAD_GEOTAGS,
                download_comments=self.config.INSTAGRAM_DOWNLOAD_COMMENTS,
                save_metadata=self.config.INSTAGRAM_SAVE_METADATA,
                compress_json=self.config.INSTAGRAM_COMPRESS_JSON,
                
                # Filename and directory patterns
                dirname_pattern=self.config.INSTAGRAM_DIRNAME_PATTERN,
                filename_pattern=self.config.INSTAGRAM_FILENAME_PATTERN,
                title_pattern=self.config.INSTAGRAM_TITLE_PATTERN,
                
                # Network configuration
                max_connection_attempts=self.config.INSTAGRAM_MAX_CONNECTION_ATTEMPTS,
                request_timeout=self.config.INSTAGRAM_REQUEST_TIMEOUT,
                
                # Resume and progress options
                resume_prefix=self.config.INSTAGRAM_RESUME_PREFIX,
                check_resume_btime=self.config.INSTAGRAM_CHECK_RESUME_BTIME,
                
                # Advanced options
                slide=self.config.INSTAGRAM_SLIDE,
                fast_update=self.config.INSTAGRAM_FAST_UPDATE,
                iphone_support=self.config.INSTAGRAM_IPHONE_SUPPORT,
                sanitize_paths=self.config.INSTAGRAM_SANITIZE_PATHS,
                
                # Rate limiting
                rate_controller=self._get_rate_controller(),
                
                # Metadata options
                post_metadata_txt_pattern="",
                storyitem_metadata_txt_pattern=""
            )
            
            # Get context for API calls
            self.context = self.loader.context
            
            # Login if credentials provided
            self._handle_authentication()
            
            self.logger.info("Instagram service initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Instagram service: {e}")
            # Fallback with minimal configuration
            self.loader = instaloader.Instaloader(
                download_videos=True,
                save_metadata=False,
                compress_json=False
            )
            self.context = self.loader.context
    
    def _get_rate_controller(self):
        """Get rate controller based on configuration"""
        rate_setting = self.config.INSTAGRAM_RATE_CONTROLLER.lower()
        
        if rate_setting == "default":
            return None
        elif rate_setting == "disabled":
            return lambda query_type: None
        else:
            # Default conservative rate controller
            def conservative_rate_controller(query_type):
                if query_type in ['login', 'logout']:
                    return 1.0
                elif query_type in ['post', 'story']:
                    return 2.0
                else:
                    return 3.0
            return conservative_rate_controller
    
    def _handle_authentication(self):
        """Handle Instagram authentication with session management"""
        
        if not self.config.INSTAGRAM_USERNAME or not self.config.INSTAGRAM_PASSWORD:
            self.logger.info("No Instagram credentials provided, using anonymous access")
            return
        
        try:
            session_file_path = Path(self.config.INSTAGRAM_SESSION_FILE)
            
            # Try to load existing session
            if session_file_path.exists():
                try:
                    self.loader.load_session_from_file(
                        self.config.INSTAGRAM_USERNAME,
                        str(session_file_path)
                    )
                    
                    # Test session validity
                    profile = instaloader.Profile.from_username(self.context, self.config.INSTAGRAM_USERNAME)
                    _ = profile.userid  # This will fail if session is invalid
                    
                    self.logger.info("Loaded Instagram session from file")
                    return
                    
                except Exception as e:
                    self.logger.warning(f"Existing session invalid: {e}")
                    # Remove invalid session file
                    session_file_path.unlink(missing_ok=True)
            
            # Create new session
            self.logger.info("Creating new Instagram session")
            self.loader.login(
                self.config.INSTAGRAM_USERNAME,
                self.config.INSTAGRAM_PASSWORD
            )
            
            # Save session for future use
            session_file_path.parent.mkdir(parents=True, exist_ok=True)
            self.loader.save_session_to_file(str(session_file_path))
            
            self.logger.info("Instagram authentication successful")
            
        except instaloader.exceptions.BadCredentialsException:
            self.logger.error("Invalid Instagram credentials")
        except instaloader.exceptions.TwoFactorAuthRequiredException:
            self.logger.error("Two-factor authentication required for Instagram")
        except instaloader.exceptions.ConnectionException as e:
            self.logger.error(f"Instagram connection error: {e}")
        except Exception as e:
            self.logger.error(f"Instagram authentication failed: {e}")
    
    def _extract_post_metadata(self, post: instaloader.Post) -> Dict[str, Any]:
        """Extract comprehensive metadata from Instagram post"""
        
        try:
            return {
                'shortcode': post.shortcode,
                'media_id': post.mediaid,
                'title': post.title or "",
                'caption': post.caption or "",
                'hashtags': list(post.caption_hashtags) if post.caption_hashtags else [],
                'mentions': list(post.caption_mentions) if post.caption_mentions else [],
                'likes': post.likes,
                'comments': post.comments,
                'date_utc': post.date_utc.isoformat() if post.date_utc else "",
                'date_local': post.date_local.isoformat() if post.date_local else "",
                'owner_username': post.owner_username,
                'owner_id': post.owner_id,
                'is_video': post.is_video,
                'typename': post.typename,
                'url': f"https://instagram.com/p/{post.shortcode}/",
                'video_duration': post.video_duration if post.is_video else None,
                'video_view_count': post.video_view_count if post.is_video else None,
                'is_sponsored': post.is_sponsored,
                'location': post.location.name if post.location else None,
                'tagged_users': [user.username for user in post.tagged_users] if post.tagged_users else [],
                'sidecar_nodes': len(list(post.get_sidecar_nodes())) if post.typename == 'GraphSidecar' else 0,
                'accessibility_caption': post.accessibility_caption or ""
            }
        except Exception as e:
            self.logger.warning(f"Error extracting post metadata: {e}")
            return {
                'shortcode': getattr(post, 'shortcode', ''),
                'owner_username': getattr(post, 'owner_username', ''),
                'is_video': getattr(post, 'is_video', False),
                'typename': getattr(post, 'typename', ''),
                'error': str(e)
            }
    
    async def download(self, url: str, output_path: str) -> Dict[str, Any]:
        """Download Instagram post/reel with complete functionality"""
        
        try:
            # Extract shortcode from URL
            shortcode = URLParser.extract_instagram_shortcode(url)
            if not shortcode:
                raise ValueError("Invalid Instagram URL - could not extract shortcode")
            
            self.logger.info(f"Downloading Instagram content: {shortcode}")
            
            # Create output directory
            output_dir = Path(output_path)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Get post object from Instagram
            post = instaloader.Post.from_shortcode(self.context, shortcode)
            
            # Extract comprehensive metadata
            metadata = self._extract_post_metadata(post)
            
            # Use temporary directory for download
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                try:
                    # Download post to temporary directory
                    # This uses instaloader's full download capability
                    self.loader.download_post(post, target=str(temp_path))
                    
                    # Find all downloaded files
                    downloaded_files = []
                    temp_files = list(temp_path.rglob("*"))
                    
                    for temp_file in temp_files:
                        if temp_file.is_file() and not temp_file.name.startswith('.'):
                            # Create meaningful filename
                            final_filename = self._create_final_filename(temp_file, post, metadata)
                            final_path = output_dir / final_filename
                            
                            # Move file to final destination
                            shutil.move(str(temp_file), str(final_path))
                            downloaded_files.append(str(final_path))
                            
                            self.logger.debug(f"Moved file: {temp_file.name} -> {final_filename}")
                    
                    if not downloaded_files:
                        raise ValueError("No files were downloaded by instaloader")
                    
                    # Update metadata with file information
                    metadata.update({
                        'files_downloaded': len(downloaded_files),
                        'download_path': str(output_dir),
                        'total_size': sum(Path(f).stat().st_size for f in downloaded_files if Path(f).exists())
                    })
                    
                    self.logger.info(f"Instagram download completed: {len(downloaded_files)} files")
                    
                    return {
                        'success': True,
                        'files': downloaded_files,
                        'metadata': metadata,
                        'platform': 'instagram'
                    }
                    
                except instaloader.exceptions.InstaloaderException as e:
                    raise ValueError(f"Instaloader error: {e}")
                
        except instaloader.exceptions.PostChangedException:
            error_msg = "Instagram post has been modified or deleted"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'files': [],
                'platform': 'instagram'
            }
            
        except instaloader.exceptions.PrivateProfileNotFollowedException:
            error_msg = "Cannot access private Instagram profile"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'files': [],
                'platform': 'instagram'
            }
            
        except instaloader.exceptions.LoginRequiredException:
            error_msg = "Instagram login required for this content"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'files': [],
                'platform': 'instagram'
            }
            
        except Exception as e:
            self.logger.error(f"Instagram download failed for {url}: {e}")
            return {
                'success': False,
                'error': str(e),
                'files': [],
                'platform': 'instagram'
            }
    
    def _create_final_filename(self, temp_file: Path, post: instaloader.Post, metadata: Dict[str, Any]) -> str:
        """Create meaningful filename for downloaded content"""
        
        try:
            # Get file extension
            extension = temp_file.suffix
            
            # Create base filename from metadata
            timestamp = metadata.get('date_utc', '').replace(':', '-').replace('T', '_')[:19]
            username = metadata.get('owner_username', 'unknown')
            shortcode = metadata.get('shortcode', 'unknown')
            
            # Handle different content types
            if post.typename == 'GraphVideo':
                content_type = 'video'
            elif post.typename == 'GraphImage':
                content_type = 'image'
            elif post.typename == 'GraphSidecar':
                content_type = 'carousel'
            else:
                content_type = 'media'
            
            # Create filename pattern
            if timestamp:
                filename = f"{username}_{timestamp}_{shortcode}_{content_type}{extension}"
            else:
                filename = f"{username}_{shortcode}_{content_type}{extension}"
            
            # Handle potential duplicates by checking original filename
            original_name = temp_file.stem
            if original_name and original_name not in filename:
                # If original has specific info (like _1, _2 for carousel), preserve it
                if '_' in original_name and original_name.split('_')[-1].isdigit():
                    suffix = '_' + original_name.split('_')[-1]
                    filename = filename.replace(extension, f"{suffix}{extension}")
            
            return filename
            
        except Exception as e:
            self.logger.warning(f"Error creating filename: {e}")
            # Fallback to original filename
            return temp_file.name
    
    def __str__(self):
        logged_in = bool(self.context and hasattr(self.context, 'username') and self.context.username)
        return f"InstagramDownloaderService(logged_in={logged_in}, loader_ready={bool(self.loader)})"
