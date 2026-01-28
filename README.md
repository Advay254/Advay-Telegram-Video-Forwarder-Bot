# Telegram Video Forwarder Bot

A lightweight, reliable Telegram bot that automatically forwards videos from one channel to another. Built with Telethon and optimized for deployment on Render.

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Support-yellow?style=for-the-badge&logo=buy-me-a-coffee)](https://www.buymeacoffee.com/Advay254)
[![GitHub](https://img.shields.io/badge/GitHub-Advay254-181717?style=for-the-badge&logo=github)](https://github.com/Advay254)
[![Telegram](https://img.shields.io/badge/Telegram-@AdvayGlimmer-26A5E4?style=for-the-badge&logo=telegram)](https://t.me/AdvayGlimmer)

## Features

✨ **Automatic Video Detection** - Monitors source channel for new video posts  
🚀 **Instant Forwarding** - Forwards videos to destination channel in real-time  
🛡️ **Reliable & Stable** - Built-in error handling and auto-reconnection  
☁️ **Cloud-Ready** - Optimized for Render deployment with web server integration  
🔒 **Secure** - Uses session strings for authentication (no phone number needed)  
📱 **Termux Compatible** - Includes scripts for mobile setup

## How It Works

```
Source Channel → Bot Detection → Automatic Forward → Destination Channel
```

The bot monitors your source channel and instantly forwards any video content to your destination channel, maintaining the original quality and metadata.

## Prerequisites

- Python 3.11+
- Telegram API credentials (API ID & API Hash)
- A Telegram account with access to both channels
- Render account (or any hosting platform)

## Quick Start

### 1. Get Telegram API Credentials

1. Visit [my.telegram.org](https://my.telegram.org)
2. Log in with your phone number
3. Go to "API Development Tools"
4. Create a new application
5. Save your `API_ID` and `API_HASH`

### 2. Generate Session String

#### On Termux (Android):

```bash
# Install required packages
pkg install python -y
pip install telethon

# Copy and paste this entire block into Termux:
cat > generate_session.py << 'EOF'
#!/usr/bin/env python3
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = '20851302'  # Replace with your API_ID
API_HASH = '4a0b97964f941eb4cc19b05fd026885e'  # Replace with your API_HASH

async def main():
    print("=== SESSION STRING GENERATOR ===\n")
    
    async with TelegramClient(StringSession(), API_ID, API_HASH) as client:
        print("Please log in...")
        await client.start()
        
        session_string = client.session.save()
        
        print("\n" + "="*70)
        print("SUCCESS! Here is your SESSION_STRING:")
        print("="*70)
        print(session_string)
        print("="*70)
        print("\nCopy this string and save it safely!")

if __name__ == "__main__":
    asyncio.run(main())
EOF

# Run the script
python generate_session.py
```

#### On Desktop:

Run this script locally to generate your session string:

```bash
pip install telethon
python generate_session.py
```

Enter your phone number when prompted and save the generated session string.

### 3. Get Channel IDs

#### On Termux (Android):

```bash
# Copy and paste this entire block into Termux:
cat > list_channels.py << 'EOF'
#!/usr/bin/env python3
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = '20851302'  # Replace with your API_ID
API_HASH = '4a0b97964f941eb4cc19b05fd026885e'  # Replace with your API_HASH
SESSION_STRING = 'YOUR_SESSION_STRING_HERE'  # Paste your session string

async def main():
    print("Connecting to Telegram...")
    client = TelegramClient(StringSession(SESSION_STRING), int(API_ID), int(API_HASH))
    
    try:
        await client.start()
        print("✓ Connected!\n")
        print("=" * 70)
        print("YOUR CHANNELS AND GROUPS")
        print("=" * 70)
        
        count = 0
        async for dialog in client.iter_dialogs():
            if dialog.is_channel or dialog.is_group:
                count += 1
                print(f"\n#{count}")
                print(f"Name: {dialog.name}")
                print(f"ID: {dialog.id}")
                
                if hasattr(dialog.entity, 'username') and dialog.entity.username:
                    print(f"Username: @{dialog.entity.username}")
                else:
                    print(f"Username: (Private)")
                
                print("-" * 70)
        
        print(f"\n✓ Found {count} channels/groups total")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
    
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
EOF

# Run the script
python list_channels.py
```

#### On Desktop:

Use the included `list_channels.py` script to find your channel IDs:

```bash
python list_channels.py
```

Copy the numeric IDs for your source and destination channels.

### 4. Deploy to Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

**Environment Variables:**
```
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
SESSION_STRING=your_session_string
SOURCE_CHANNEL=-1001234567890
DEST_CHANNEL=-1009876543210
PORT=10000
```

## Local Development

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/telegram-video-forwarder.git
cd telegram-video-forwarder
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set environment variables:**
```bash
export TELEGRAM_API_ID="your_api_id"
export TELEGRAM_API_HASH="your_api_hash"
export SESSION_STRING="your_session_string"
export SOURCE_CHANNEL="-1001234567890"
export DEST_CHANNEL="-1009876543210"
```

4. **Run the bot:**
```bash
python main.py
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `TELEGRAM_API_ID` | Your Telegram API ID | ✅ |
| `TELEGRAM_API_HASH` | Your Telegram API Hash | ✅ |
| `SESSION_STRING` | Generated session string | ✅ |
| `SOURCE_CHANNEL` | Channel ID to monitor | ✅ |
| `DEST_CHANNEL` | Channel ID to forward to | ✅ |
| `PORT` | Web server port (default: 8080) | ❌ |

### Channel ID Format

Channel IDs should be in numeric format:
- **Correct:** `-1001234567890`
- **Incorrect:** `@channelname` or `channelname`

## Troubleshooting

### "Cannot find any entity corresponding to..."

**Solution:** Ensure your account is a member of both channels and you're using the correct numeric channel IDs.

### Bot disconnects frequently

**Solution:** Regenerate your session string and update the environment variable.

### Videos not forwarding

**Checklist:**
- ✅ Bot account is a member of both channels
- ✅ Source channel ID is correct
- ✅ Destination channel allows the bot to post
- ✅ Session string is valid and not expired

## Architecture

```
┌─────────────────┐
│  Source Channel │
└────────┬────────┘
         │ New Video
         ↓
┌─────────────────┐
│   Telethon Bot  │ ← Event Handler
└────────┬────────┘
         │ Forward
         ↓
┌─────────────────┐
│  Dest Channel   │
└─────────────────┘
```

## Tech Stack

- **[Telethon](https://docs.telethon.dev/)** - Telegram client library
- **[aiohttp](https://docs.aiohttp.org/)** - Web server for health checks
- **Python 3.13** - Runtime environment
- **Render** - Deployment platform

## Security

⚠️ **Important Security Notes:**

- Never commit your `.env` file or expose credentials
- Session strings have the same access as your account - keep them secure
- Rotate session strings periodically
- Use environment variables for all sensitive data

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📫 **Issues:** [GitHub Issues](https://github.com/Advay254/Advay-Telegram-Video-Forwarder-Bot/issues)
- 📖 **Documentation:** [Telethon Docs](https://docs.telethon.dev/)
- 💬 **Telegram:** [@AdvayGlimmer](https://t.me/AdvayGlimmer)
- ☕ **Buy Me a Coffee:** [Support this project](https://www.buymeacoffee.com/Advay254)

## Acknowledgments

- Built with [Telethon](https://github.com/LonamiWebs/Telethon)
- Deployed on [Render](https://render.com)
- Inspired by the Telegram automation community

---

<div align="center">

**⭐ Star this repo if you find it useful!**

[![Buy Me A Coffee](https://img.buymeacoffee.com/button-api/?text=Buy%20me%20a%20coffee&emoji=☕&slug=Advay254&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff)](https://www.buymeacoffee.com/Advay254)

Made with ❤️ by [Advay](https://github.com/Advay254)

</div>
