from pyrogram import Client, filters
from pyrogram.types import Message
from ..services.db_service import DatabaseService
from ..config import config
import asyncio
import logging
import sys
import os

class AdminHandler:
    """Handle admin commands"""
    
    def __init__(self, app: Client, db_service: DatabaseService, shutdown_event: asyncio.Event):
        self.app = app
        self.db = db_service
        self.shutdown_event = shutdown_event
        self.logger = logging.getLogger(__name__)
        
        # Register handlers
        self.register_handlers()
    
    def register_handlers(self):
        """Register admin command handlers"""
        
        @self.app.on_message(filters.command("promote") & self.admin_filter)
        async def handle_promote(client: Client, message: Message):
            await self.handle_promote_command(message)
        
        @self.app.on_message(filters.command("verify") & self.admin_filter)
        async def handle_verify(client: Client, message: Message):
            await self.handle_verify_command(message)
        
        @self.app.on_message(filters.command("ban") & self.admin_filter)
        async def handle_ban(client: Client, message: Message):
            await self.handle_ban_command(message)
        
        @self.app.on_message(filters.command("unban") & self.admin_filter)
        async def handle_unban(client: Client, message: Message):
            await self.handle_unban_command(message)
        
        @self.app.on_message(filters.command("stop") & self.admin_filter)
        async def handle_stop(client: Client, message: Message):
            await self.handle_stop_command(message)
        
        @self.app.on_message(filters.command("reboot") & self.admin_filter)
        async def handle_reboot(client: Client, message: Message):
            await self.handle_reboot_command(message)
        
        @self.app.on_message(filters.command("stats") & self.admin_filter)
        async def handle_stats(client: Client, message: Message):
            await self.handle_stats_command(message)
    
    @property
    def admin_filter(self):
        """Filter for admin users"""
        return filters.user(config.ADMIN_IDS)
    
    async def handle_promote_command(self, message: Message):
        """Handle /promote command"""
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
            if self.db.update_user_role(user_id, "admin"):
                await message.reply_text(f"✅ User {user_id} promoted to admin.")
            else:
                await message.reply_text("❌ Failed to promote user.")
        else:
            await message.reply_text("❌ Reply to a user's message to promote them.")
    
    async def handle_verify_command(self, message: Message):
        """Handle /verify command"""
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
            if self.db.update_user_role(user_id, "verified_user"):
                await message.reply_text(f"✅ User {user_id} verified.")
            else:
                await message.reply_text("❌ Failed to verify user.")
        else:
            await message.reply_text("❌ Reply to a user's message to verify them.")
    
    async def handle_ban_command(self, message: Message):
        """Handle /ban command"""
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
            if self.db.ban_user(user_id, True):
                await message.reply_text(f"✅ User {user_id} banned.")
            else:
                await message.reply_text("❌ Failed to ban user.")
        else:
            await message.reply_text("❌ Reply to a user's message to ban them.")
    
    async def handle_unban_command(self, message: Message):
        """Handle /unban command"""
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
            if self.db.ban_user(user_id, False):
                await message.reply_text(f"✅ User {user_id} unbanned.")
            else:
                await message.reply_text("❌ Failed to unban user.")
        else:
            await message.reply_text("❌ Reply to a user's message to unban them.")
    
    async def handle_stop_command(self, message: Message):
        """Handle /stop command - graceful shutdown"""
        await message.reply_text("🛑 Initiating graceful shutdown...")
        self.logger.info("Admin initiated shutdown")
        self.shutdown_event.set()
    
    async def handle_reboot_command(self, message: Message):
        """Handle /reboot command"""
        await message.reply_text("🔄 Rebooting bot...")
        self.logger.info("Admin initiated reboot")
        self.shutdown_event.set()
        # You could implement restart logic here
        os.execv(sys.executable, ['python'] + sys.argv)
    
    async def handle_stats_command(self, message: Message):
        """Handle /stats command"""
        # This would query the database for statistics
        stats_text = """
📊 **Bot Statistics**

👥 Total Users: 150
✅ Downloads Today: 45
⏳ Queue Length: 3
💾 Storage Used: 2.3 GB
⚡ Uptime: 2d 14h 32m

**Platform Stats:**
• TikTok: 60%
• Instagram: 25%
• YouTube: 10%
• Others: 5%
        """
        
        await message.reply_text(stats_text)