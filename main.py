#!/usr/bin/env python3
"""
Production-Ready Telegram Video Forwarder Bot (Render Compatible)
"""

import os
import sys
import logging
import asyncio
from datetime import datetime
from aiohttp import web
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import (
    FloodWaitError, ChatWriteForbiddenError, ChannelPrivateError, 
    UserBannedInChannelError, SlowModeWaitError, MediaEmptyError, RPCError
)
from telethon.tl.types import MessageMediaDocument

# ============================================================================
# CONFIGURATION
# ============================================================================

API_ID = os.getenv('TELEGRAM_API_ID')
API_HASH = os.getenv('TELEGRAM_API_HASH')
SESSION_STRING = os.getenv('SESSION_STRING')
SOURCE_CHANNEL = os.getenv('SOURCE_CHANNEL')
DEST_CHANNEL = os.getenv('DEST_CHANNEL')
PORT = int(os.getenv('PORT', 8080))
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# ============================================================================
# LOGGING SETUP
# ============================================================================

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, LOG_LEVEL),
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# ============================================================================
# DUMMY WEB SERVER (Keep Render Alive)
# ============================================================================

async def health_check(request):
    return web.Response(text="Bot is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logger.info(f"Web server started on port {PORT}")

# ============================================================================
# BOT LOGIC
# ============================================================================

class VideoForwarderBot:
    def __init__(self):
        self.client = None

    async def start(self):
        logger.info("Starting Bot...")

        if not SESSION_STRING:
            logger.error("SESSION_STRING is missing! Set it in environment variables.")
            sys.exit(1)

        try:
            # Initialize with String Session
            self.client = TelegramClient(StringSession(SESSION_STRING), int(API_ID), API_HASH)
            await self.client.start()
            
            logger.info("✓ Logged in successfully using Session String")
            
            # FIX: Fetch the entities to populate the session cache
            # Try multiple methods to ensure entities are loaded
            try:
                # Method 1: Direct get_entity
                logger.info("Fetching source channel...")
                source_entity = await self.client.get_entity(int(SOURCE_CHANNEL))
                logger.info(f"✓ Successfully loaded source: {source_entity.title}")
                
                logger.info("Fetching destination channel...")
                dest_entity = await self.client.get_entity(int(DEST_CHANNEL))
                logger.info(f"✓ Successfully loaded destination: {dest_entity.title}")
                
                # Method 2: Ensure they're in the session by getting input entities
                await self.client.get_input_entity(int(SOURCE_CHANNEL))
                await self.client.get_input_entity(int(DEST_CHANNEL))
                
            except Exception as e:
                logger.error(f"Failed to load channel entities: {e}")
                logger.error("Make sure your account has access to both channels and the IDs are correct")
                sys.exit(1)
            
            # Register handlers (now the entities are cached)
            self.client.add_event_handler(self.handle_message, events.NewMessage(chats=int(SOURCE_CHANNEL)))
            logger.info(f"✓ Monitoring source: {SOURCE_CHANNEL}")
            
            # Keep running
            await self.client.run_until_disconnected()

        except Exception as e:
            logger.error(f"Critical Error: {e}", exc_info=True)
            sys.exit(1)

    async def handle_message(self, event):
        try:
            # Check for video
            is_video = False
            if event.message.video:
                is_video = True
            elif isinstance(event.message.media, MessageMediaDocument):
                if event.message.media.document.mime_type.startswith('video/'):
                    is_video = True
            
            if is_video:
                logger.info(f"Video detected in {SOURCE_CHANNEL}, forwarding...")
                await event.message.forward_to(DEST_CHANNEL)
                logger.info("✓ Forwarded successfully")

        except Exception as e:
            logger.error(f"Error forwarding: {e}")

# ============================================================================
# MAIN
# ============================================================================

async def main():
    bot = VideoForwarderBot()
    # Start web server first (to satisfy Render)
    await start_web_server()
    # Start bot
    await bot.start()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
