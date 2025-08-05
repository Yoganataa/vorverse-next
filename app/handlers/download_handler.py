from pyrogram import Client, filters
from pyrogram.types import Message
from ..services.db_service import DatabaseService
from ..utils.url_parser import URLParser
from ..config import config
import asyncio
import logging
from typing import Dict, Any

class DownloadHandler:
    """Handle user download requests"""
    
    def __init__(self, app: Client, db_service: DatabaseService, download_queue: asyncio.Queue):
        self.app = app
        self.db = db_service
        self.download_queue = download_queue
        self.logger = logging.getLogger(__name__)
        
        # Register handlers
        self.register_handlers()
    
    def register_handlers(self):
        """Register message handlers"""
        
        @self.app.on_message(filters.text & filters.private)
        async def handle_download_request(client: Client, message: Message):
            await self.process_download_request(message)
        
        @self.app.on_message(filters.command("start"))
        async def handle_start(client: Client, message: Message):
            await self.handle_start_command(message)
        
        @self.app.on_message(filters.command("help"))
        async def handle_help(client: Client, message: Message):
            await self.handle_help_command(message)
    
    async def handle_start_command(self, message: Message):
        """Handle /start command"""
        user = self.db.get_or_create_user(
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
            message.from_user.last_name
        )
        
        welcome_text = """
🎬 **Ultimate Media Downloader Bot**

Send me a URL from any supported platform and I'll download it for you!

**Supported Platforms:**
• TikTok & Douyin
• Instagram (Posts, Reels, IGTV)
• YouTube (Videos, Shorts)
• Twitter/X
• Facebook

**Features:**
• High-quality downloads
• Batch URL processing
• Resume capability
• Advanced error handling

Just paste a URL and I'll handle the rest! 🚀
        """
        
        await message.reply_text(welcome_text)
    
    async def handle_help_command(self, message: Message):
        """Handle /help command"""
        help_text = """
📋 **How to use:**

1. Send me any supported URL
2. Wait for processing
3. Receive your downloaded media

**Supported URL formats:**
• `https://tiktok.com/@user/video/123`
• `https://instagram.com/p/ABC123/`
• `https://youtube.com/watch?v=ABC123`
• `https://twitter.com/user/status/123`
• And many more!

**Tips:**
• You can send multiple URLs at once
• Use /status to check your download history
• Report issues to admins if needed

Need more help? Contact support!
        """
        
        await message.reply_text(help_text)
    
    async def process_download_request(self, message: Message):
        """Process download request"""
        
        # Check if user is banned
        if self.db.is_user_banned(message.from_user.id):
            await message.reply_text("❌ You are banned from using this bot.")
            return
        
        # Update user info
        self.db.get_or_create_user(
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
            message.from_user.last_name
        )
        
        # Extract URLs from message
        urls = URLParser.extract_urls(message.text)
        
        if not urls:
            await message.reply_text(
                "❌ No supported URLs found in your message.\n"
                "Send /help to see supported platforms."
            )
            return
        
        # Process each URL
        processing_msg = await message.reply_text(
            f"⏳ Processing {len(urls)} URL(s)..."
        )
        
        for url, platform in urls:
            try:
                # Create download record
                record_id = self.db.create_download_record(
                    message.from_user.id,
                    url,
                    platform
                )
                
                # Add to queue
                task_data = {
                    'record_id': record_id,
                    'user_id': message.from_user.id,
                    'chat_id': message.chat.id,
                    'message_id': message.id,
                    'url': url,
                    'platform': platform
                }
                
                await self.download_queue.put(task_data)
                self.logger.info(f"Queued download: {url} for user {message.from_user.id}")
                
            except Exception as e:
                self.logger.error(f"Error queuing download {url}: {e}")
                await message.reply_text(f"❌ Error processing {url}: {str(e)}")
        
        await processing_msg.edit_text(
            f"✅ {len(urls)} download(s) added to queue!\n"
            "You'll receive the files when ready."
        )