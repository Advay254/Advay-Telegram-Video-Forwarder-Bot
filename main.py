#!/usr/bin/env python3
"""
Simple & Reliable Telegram Video Forwarder
Forwards videos from one channel to another with minimal complexity
"""
import os
import sys
import logging
import asyncio
from aiohttp import web
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# Configuration
API_ID = int(os.getenv('TELEGRAM_API_ID'))
API_HASH = os.getenv('TELEGRAM_API_HASH')
SESSION_STRING = os.getenv('SESSION_STRING')
SOURCE_CHANNEL = int(os.getenv('SOURCE_CHANNEL'))
DEST_CHANNEL = int(os.getenv('DEST_CHANNEL'))
PORT = int(os.getenv('PORT', 8080))

# Logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Web server for Render
async def health_check(request):
    return web.Response(text="✓ Bot is running")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logger.info(f"Web server on port {PORT}")

# Main bot
async def main():
    # Start web server
    await start_web_server()
    
    # Create client
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
    
    # Connect
    await client.start()
    logger.info("✓ Connected to Telegram")
    
    # Define message handler
    @client.on(events.NewMessage(chats=SOURCE_CHANNEL))
    async def handler(event):
        try:
            # Check if message has video
            if event.message.video or (event.message.document and 
                event.message.document.mime_type and 
                event.message.document.mime_type.startswith('video/')):
                
                logger.info(f"Video detected, forwarding...")
                await client.forward_messages(DEST_CHANNEL, event.message)
                logger.info("✓ Video forwarded")
                
        except Exception as e:
            logger.error(f"Error: {e}")
    
    logger.info(f"✓ Monitoring channel {SOURCE_CHANNEL}")
    logger.info("Bot is ready!")
    
    # Keep running
    await client.run_until_disconnected()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Stopped")
