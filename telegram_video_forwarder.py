#!/usr/bin/env python3
"""
Production-Ready Telegram Video Forwarding Bot
Forwards videos from a source channel to a destination channel using Telethon.
Designed for 24/7 operation with comprehensive error handling and recovery.
"""

import os
import sys
import logging
import asyncio
from datetime import datetime
from telethon import TelegramClient, events
from telethon.errors import (
    SessionPasswordNeededError,
    FloodWaitError,
    ChatWriteForbiddenError,
    ChannelPrivateError,
    UserBannedInChannelError,
    SlowModeWaitError,
    MediaEmptyError,
    MessageNotModifiedError,
    RPCError
)
from telethon.tl.types import MessageMediaDocument, MessageMediaPhoto

# ============================================================================
# CONFIGURATION - Set via environment variables
# ============================================================================

# Telegram API credentials (get from https://my.telegram.org)
API_ID = os.getenv('TELEGRAM_API_ID')
API_HASH = os.getenv('TELEGRAM_API_HASH')

# Phone number in international format (e.g., +1234567890)
PHONE_NUMBER = os.getenv('TELEGRAM_PHONE_NUMBER')

# Source channel username or ID (e.g., 'channelusername' or '-100123456789')
SOURCE_CHANNEL = os.getenv('SOURCE_CHANNEL')

# Destination channel username or ID (e.g., 'yourchannel' or '-100987654321')
DEST_CHANNEL = os.getenv('DEST_CHANNEL')

# Optional: 2FA password if your account has it enabled
TWO_FA_PASSWORD = os.getenv('TELEGRAM_2FA_PASSWORD', None)

# Session name (will create a .session file - keep this safe!)
SESSION_NAME = os.getenv('SESSION_NAME', 'video_forwarder_session')

# Logging level
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Maximum retry attempts for failed operations
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))

# Delay between retries (seconds)
RETRY_DELAY = int(os.getenv('RETRY_DELAY', '5'))

# ============================================================================
# VALIDATION
# ============================================================================

def validate_config():
    """Validate all required environment variables are set."""
    required_vars = {
        'TELEGRAM_API_ID': API_ID,
        'TELEGRAM_API_HASH': API_HASH,
        'TELEGRAM_PHONE_NUMBER': PHONE_NUMBER,
        'SOURCE_CHANNEL': SOURCE_CHANNEL,
        'DEST_CHANNEL': DEST_CHANNEL
    }
    
    missing = [key for key, value in required_vars.items() if not value]
    
    if missing:
        print("ERROR: Missing required environment variables:")
        for var in missing:
            print(f"  - {var}")
        print("\nPlease set all required environment variables and try again.")
        sys.exit(1)
    
    # Validate API_ID is numeric
    try:
        int(API_ID)
    except ValueError:
        print("ERROR: TELEGRAM_API_ID must be a numeric value")
        sys.exit(1)

# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging():
    """Configure comprehensive logging with rotation."""
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Configure logging format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Set up file handler
    file_handler = logging.FileHandler(
        f'logs/forwarder_{datetime.now().strftime("%Y%m%d")}.log',
        encoding='utf-8'
    )
    file_handler.setLevel(getattr(logging, LOG_LEVEL))
    file_handler.setFormatter(logging.Formatter(log_format, date_format))
    
    # Set up console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, LOG_LEVEL))
    console_handler.setFormatter(logging.Formatter(log_format, date_format))
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        handlers=[file_handler, console_handler]
    )
    
    # Reduce Telethon's logging verbosity
    logging.getLogger('telethon').setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)

# ============================================================================
# BOT CLASS
# ============================================================================

class VideoForwarderBot:
    """Production-ready Telegram video forwarding bot."""
    
    def __init__(self):
        """Initialize the bot with configuration."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.client = None
        self.is_running = False
        self.forwarded_count = 0
        self.error_count = 0
        self.start_time = datetime.now()
        
    async def start(self):
        """Start the bot and connect to Telegram."""
        self.logger.info("Starting Telegram Video Forwarder Bot...")
        self.logger.info(f"Source Channel: {SOURCE_CHANNEL}")
        self.logger.info(f"Destination Channel: {DEST_CHANNEL}")
        
        try:
            # Initialize Telegram client
            self.client = TelegramClient(
                SESSION_NAME,
                int(API_ID),
                API_HASH,
                connection_retries=MAX_RETRIES,
                retry_delay=RETRY_DELAY
            )
            
            # Connect and authenticate
            await self.client.start(
                phone=PHONE_NUMBER,
                password=TWO_FA_PASSWORD
            )
            
            self.logger.info("Successfully connected to Telegram")
            
            # Verify access to channels
            await self._verify_channels()
            
            # Register event handler
            self._register_handlers()
            
            self.is_running = True
            self.logger.info("Bot is now running and monitoring for videos...")
            self.logger.info("Press Ctrl+C to stop")
            
            # Keep the bot running
            await self.client.run_until_disconnected()
            
        except SessionPasswordNeededError:
            self.logger.error("Two-factor authentication is enabled. Please set TELEGRAM_2FA_PASSWORD")
            sys.exit(1)
        except Exception as e:
            self.logger.error(f"Failed to start bot: {e}", exc_info=True)
            sys.exit(1)
    
    async def _verify_channels(self):
        """Verify bot has access to both source and destination channels."""
        try:
            # Check source channel
            source_entity = await self.client.get_entity(SOURCE_CHANNEL)
            self.logger.info(f"✓ Source channel verified: {source_entity.title}")
            
            # Check destination channel
            dest_entity = await self.client.get_entity(DEST_CHANNEL)
            self.logger.info(f"✓ Destination channel verified: {dest_entity.title}")
            
            # Check if we can post to destination
            try:
                # Get channel permissions
                participant = await self.client.get_permissions(dest_entity, 'me')
                if not participant.is_admin and not participant.post_messages:
                    self.logger.warning("Warning: May not have permission to post in destination channel")
            except:
                pass  # Channel might be our own
                
        except ChannelPrivateError:
            self.logger.error("Cannot access one of the channels. Make sure you're a member.")
            sys.exit(1)
        except ValueError as e:
            self.logger.error(f"Invalid channel username/ID: {e}")
            sys.exit(1)
        except Exception as e:
            self.logger.error(f"Error verifying channels: {e}", exc_info=True)
            sys.exit(1)
    
    def _register_handlers(self):
        """Register event handlers for new messages."""
        
        @self.client.on(events.NewMessage(chats=SOURCE_CHANNEL))
        async def handler(event):
            """Handle new messages from source channel."""
            try:
                # Check if message contains video
                if not event.message.media:
                    return
                
                is_video = False
                media_type = None
                
                # Check for video in document
                if isinstance(event.message.media, MessageMediaDocument):
                    if event.message.media.document.mime_type:
                        mime = event.message.media.document.mime_type
                        if mime.startswith('video/'):
                            is_video = True
                            media_type = 'video (document)'
                
                # Some videos might be sent as media
                if hasattr(event.message, 'video') and event.message.video:
                    is_video = True
                    media_type = 'video'
                
                if not is_video:
                    return
                
                self.logger.info(f"New {media_type} detected from {SOURCE_CHANNEL}")
                
                # Forward the video with retry logic
                await self._forward_with_retry(event.message)
                
            except Exception as e:
                self.logger.error(f"Error in message handler: {e}", exc_info=True)
                self.error_count += 1
    
    async def _forward_with_retry(self, message, attempt=1):
        """Forward message with exponential backoff retry logic."""
        try:
            # Forward the message
            await self.client.forward_messages(
                entity=DEST_CHANNEL,
                messages=message,
                from_peer=SOURCE_CHANNEL
            )
            
            self.forwarded_count += 1
            self.logger.info(
                f"✓ Video forwarded successfully "
                f"(Total: {self.forwarded_count}, Errors: {self.error_count})"
            )
            
        except FloodWaitError as e:
            # Telegram rate limit - wait required time
            wait_time = e.seconds
            self.logger.warning(f"Rate limited. Waiting {wait_time} seconds...")
            await asyncio.sleep(wait_time)
            
            # Retry after waiting
            if attempt < MAX_RETRIES:
                await self._forward_with_retry(message, attempt + 1)
            else:
                self.logger.error(f"Failed to forward after {MAX_RETRIES} attempts")
                self.error_count += 1
                
        except SlowModeWaitError as e:
            # Destination channel has slow mode enabled
            wait_time = e.seconds
            self.logger.warning(f"Slow mode active. Waiting {wait_time} seconds...")
            await asyncio.sleep(wait_time)
            
            if attempt < MAX_RETRIES:
                await self._forward_with_retry(message, attempt + 1)
            else:
                self.logger.error(f"Failed to forward after {MAX_RETRIES} attempts")
                self.error_count += 1
                
        except ChatWriteForbiddenError:
            self.logger.error("No permission to write in destination channel")
            self.error_count += 1
            
        except UserBannedInChannelError:
            self.logger.error("User is banned in destination channel")
            self.error_count += 1
            
        except MediaEmptyError:
            self.logger.error("Media is empty or corrupted")
            self.error_count += 1
            
        except RPCError as e:
            # Generic Telegram API error
            self.logger.error(f"Telegram API error: {e}")
            
            # Retry with exponential backoff
            if attempt < MAX_RETRIES:
                delay = RETRY_DELAY * (2 ** (attempt - 1))  # Exponential backoff
                self.logger.info(f"Retrying in {delay} seconds... (Attempt {attempt}/{MAX_RETRIES})")
                await asyncio.sleep(delay)
                await self._forward_with_retry(message, attempt + 1)
            else:
                self.logger.error(f"Failed to forward after {MAX_RETRIES} attempts")
                self.error_count += 1
                
        except Exception as e:
            self.logger.error(f"Unexpected error during forwarding: {e}", exc_info=True)
            self.error_count += 1
    
    async def stop(self):
        """Gracefully stop the bot."""
        self.logger.info("Stopping bot...")
        self.is_running = False
        
        # Log statistics
        uptime = datetime.now() - self.start_time
        self.logger.info(f"Bot Statistics:")
        self.logger.info(f"  Uptime: {uptime}")
        self.logger.info(f"  Videos Forwarded: {self.forwarded_count}")
        self.logger.info(f"  Errors: {self.error_count}")
        
        if self.client:
            await self.client.disconnect()
        
        self.logger.info("Bot stopped successfully")

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

async def main():
    """Main entry point for the bot."""
    
    # Validate configuration
    validate_config()
    
    # Setup logging
    logger = setup_logging()
    
    # Create and start bot
    bot = VideoForwarderBot()
    
    try:
        await bot.start()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
        await bot.stop()
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        await bot.stop()
        sys.exit(1)

if __name__ == '__main__':
    # Run the bot
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped by user")
        sys.exit(0)
