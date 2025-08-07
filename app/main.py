import asyncio
import logging
import signal
import sys
from pathlib import Path
from pyrogram import Client
import zipfile
import tempfile
import shutil
from typing import Dict, Any, Optional
import importlib
import inspect

# Konfigurasi dan handler diimpor seperti biasa
from .config import config
from .services.db_service import DatabaseService
from .handlers.download_handler import DownloadHandler
from .handlers.admin_handler import AdminHandler
from .utils.url_parser import URLParser

# Konfigurasi logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL, "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class MediaDownloaderBot:
    """Main bot application class"""

    def __init__(self):
        self.app = None
        self.db_service = None
        self.services = {}
        self.download_queue = asyncio.Queue()
        self.shutdown_event = asyncio.Event()
        self.download_semaphore = asyncio.Semaphore(config.MAX_CONCURRENT_DOWNLOADS)
        self.running_tasks = set()
        self.config = config  # Memberikan akses config ke metode kelas
        self.logger = logger  # Memberikan akses logger ke metode kelas

    def setup_bot(self):
        """Initialize bot and services with dynamic discovery."""
        
        # Inisialisasi klien Pyrogram
        self.app = Client(
            "media_downloader_bot",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            workdir="./data"
        )
        
        # Inisialisasi layanan database
        self.db_service = DatabaseService(config.DATABASE_URL)
        
        # --- PERUBAHAN UTAMA DIMULAI DI SINI ---
        # Menggunakan penemuan layanan dinamis, bukan pendaftaran manual
        self.services = self._discover_services()
        # --- PERUBAHAN UTAMA SELESAI DI SINI ---
        
        # Inisialisasi handler
        self.download_handler = DownloadHandler(self.app, self.db_service, self.download_queue)
        self.admin_handler = AdminHandler(self.app, self.db_service, self.shutdown_event)
        
        logger.info("Bot setup completed with dynamic service discovery")

    # ▼▼▼ FUNGSI REVISI DITERAPKAN DI SINI ▼▼▼
    
    def _discover_services(self) -> Dict[str, Any]:
        """
        REVISED: Dynamic service discovery from app/services/ directory
        Automatically scans and registers all *_service.py files
        """
        services = {}
        services_dir = Path(__file__).parent / "services"
        self.logger.info("Starting dynamic service discovery...")
        
        try:
            service_files = list(services_dir.glob("*_service.py"))
            
            for service_file in service_files:
                try:
                    if service_file.name in ["base_downloader.py", "__init__.py"]:
                        continue
                    
                    module_name = service_file.stem
                    service_name = module_name.replace("_service", "")
                    module_path = f"app.services.{module_name}"
                    module = importlib.import_module(module_path)
                    
                    service_class = None
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if name.endswith('Service') and name != 'BaseDownloader' and hasattr(obj, 'download'):
                            service_class = obj
                            break
                            
                    if service_class:
                        service_instance = service_class(self.config)
                        services[service_name] = service_instance
                        
                        if service_name == "tiktok":
                            services["douyin"] = service_instance
                        elif service_name == "ytdlp":
                            fallback_platforms = ["youtube", "twitter", "facebook", "generic"]
                            for platform in fallback_platforms:
                                if platform not in services:
                                    services[platform] = service_instance
                                    
                        self.logger.info(f"Registered service: {service_name} -> {service_class.__name__}")
                    else:
                        self.logger.warning(f"No valid service class found in {module_name}")
                        
                except ImportError as e:
                    self.logger.error(f"Failed to import {service_file.name}: {e}")
                except Exception as e:
                    self.logger.error(f"Error processing {service_file.name}: {e}")
                    
            self.logger.info(f"Service discovery completed. Registered {len(services)} services")
            for platform, service in services.items():
                self.logger.debug(f"  {platform} -> {service.__class__.__name__}")
                
            return services
            
        except Exception as e:
            self.logger.error(f"Service discovery failed: {e}")
            return {}

    def get_service_for_url(self, url: str) -> Optional[Any]:
        """
        REVISED: Get appropriate downloader service for URL with dynamic service support
        """
        try:
            platform = URLParser.detect_platform(url)
            
            if not platform:
                self.logger.warning(f"Unknown platform for URL: {url}")
                return self.services.get('generic')
                
            service = self.services.get(platform)
            
            if service:
                self.logger.debug(f"Selected service for {platform}: {service.__class__.__name__}")
                return service
                
            generic_service = self.services.get('generic')
            if generic_service:
                self.logger.info(f"Using generic service for unsupported platform: {platform}")
                return generic_service
                
            self.logger.error(f"No service available for platform: {platform}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting service for URL {url}: {e}")
            return self.services.get('generic')
            
    # ▲▲▲ FUNGSI REVISI SELESAI DI SINI ▲▲▲

    # ▼▼▼ SISA KODE ASLI (TIDAK BERUBAH) ▼▼▼

    async def process_download_task(self, task_data: Dict[str, Any]):
        """Process individual download task"""
        
        async with self.download_semaphore:
            record_id = task_data['record_id']
            user_id = task_data['user_id']
            chat_id = task_data['chat_id']
            url = task_data['url']
            platform = task_data['platform']
            
            try:
                service = self.get_service_for_url(url)
                if not service:
                    raise ValueError(f"No service available for platform: {platform}")
                
                output_dir = Path(config.DOWNLOAD_PATH) / str(user_id) / str(record_id)
                output_dir.mkdir(parents=True, exist_ok=True)
                
                async with service:
                    result = await service.download(url, str(output_dir))
                
                if result['success']:
                    total_size = sum(Path(f).stat().st_size for f in result['files'] if Path(f).exists())
                    self.db_service.update_download_record(
                        record_id,
                        'completed',
                        str(output_dir),
                        total_size
                    )
                    await self.send_files_to_user(chat_id, result['files'], result.get('metadata', {}))
                    logger.info(f"Download completed: {url} for user {user_id}")
                else:
                    error_msg = result.get('error', 'Unknown error')
                    self.db_service.update_download_record(
                        record_id,
                        'failed',
                        error_message=error_msg
                    )
                    await self.app.send_message(
                        chat_id,
                        f"❌ Download failed for {url}\nError: {error_msg}"
                    )
                    logger.error(f"Download failed: {url} - {error_msg}")
            
            except Exception as e:
                self.db_service.update_download_record(
                    record_id,
                    'failed',
                    error_message=str(e)
                )
                try:
                    await self.app.send_message(
                        chat_id,
                        f"❌ Download failed for {url}\nError: {str(e)}"
                    )
                except Exception:
                    pass
                logger.error(f"Download task failed: {url} - {e}", exc_info=True)
            
            finally:
                # Menggunakan delay dari config
                asyncio.create_task(self.cleanup_user_files(user_id, record_id, delay_hours=config.CLEANUP_DELAY_HOURS))

    async def send_files_to_user(self, chat_id: int, files: list, metadata: Dict[str, Any]):
        """Send downloaded files to user"""
        
        try:
            if not files:
                await self.app.send_message(chat_id, "❌ No files were downloaded.")
                return
            
            caption = f"✅ {metadata.get('title') or metadata.get('caption') or 'Media Downloaded'}"
            
            if len(files) > 1:
                with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as zip_file:
                    with zipfile.ZipFile(zip_file.name, 'w') as zf:
                        for file_path in files:
                            if Path(file_path).exists():
                                zf.write(file_path, Path(file_path).name)
                    
                    await self.app.send_document(
                        chat_id,
                        zip_file.name,
                        caption=f"✅ Downloaded: {metadata.get('title', 'Media files')} ({len(files)} files)"
                    )
                    Path(zip_file.name).unlink(missing_ok=True)
            
            else:
                file_path_str = files[0]
                if Path(file_path_str).exists():
                    if any(file_path_str.lower().endswith(ext) for ext in ['.mp4', '.avi', '.mov', '.mkv']):
                        await self.app.send_video(chat_id, file_path_str, caption=caption)
                    elif any(file_path_str.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                        await self.app.send_photo(chat_id, file_path_str, caption=caption)
                    else:
                        await self.app.send_document(chat_id, file_path_str, caption=caption)
        
        except Exception as e:
            logger.error(f"Error sending files to {chat_id}: {e}", exc_info=True)
            await self.app.send_message(
                chat_id,
                f"❌ Error sending files: {str(e)}"
            )

    async def cleanup_user_files(self, user_id: int, record_id: int, delay_hours: int = 24):
        """Cleanup user files after delay"""
        await asyncio.sleep(delay_hours * 3600)
        
        try:
            user_dir = Path(config.DOWNLOAD_PATH) / str(user_id) / str(record_id)
            if user_dir.exists():
                shutil.rmtree(user_dir)
                logger.info(f"Cleaned up files for user {user_id}, record {record_id}")
        except Exception as e:
            logger.error(f"Error cleaning up files for user {user_id}: {e}")

    async def queue_worker(self):
        """Main queue worker for processing downloads"""
        logger.info("Queue worker started")
        
        while not self.shutdown_event.is_set():
            try:
                task_data = await asyncio.wait_for(
                    self.download_queue.get(),
                    timeout=1.0
                )
                task = asyncio.create_task(self.process_download_task(task_data))
                self.running_tasks.add(task)
                task.add_done_callback(self.running_tasks.discard)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Queue worker error: {e}")
                await asyncio.sleep(1)
        
        if self.running_tasks:
            logger.info(f"Waiting for {len(self.running_tasks)} tasks to complete...")
            await asyncio.gather(*self.running_tasks, return_exceptions=True)
        
        logger.info("Queue worker stopped")

    async def start(self):
        """Start the bot"""
        logger.info("Starting Media Downloader Bot...")
        
        loop = asyncio.get_event_loop()
        for sig in [signal.SIGTERM, signal.SIGINT]:
            try:
                loop.add_signal_handler(sig, lambda: self.shutdown_event.set())
            except NotImplementedError:
                pass
        
        await self.app.start()
        worker_task = asyncio.create_task(self.queue_worker())
        logger.info("Bot started successfully!")
        
        await self.shutdown_event.wait()
        logger.info("Shutdown signal received, stopping bot...")
        
        # Stop queue worker gracefully
        if not worker_task.done():
            worker_task.cancel()
            try:
                await worker_task
            except asyncio.CancelledError:
                logger.info("Queue worker task cancelled.")
        
        await self.app.stop()
        logger.info("Bot stopped gracefully")


async def main():
    """Main entry point"""
    bot = MediaDownloaderBot()
    bot.setup_bot()
    await bot.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}", exc_info=True)
        sys.exit(1)