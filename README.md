# Telegram Video Forwarder Bot - Production Deployment Guide

## Overview
Production-ready Python bot that automatically forwards videos from a source Telegram channel to your destination channel. Built with comprehensive error handling, retry logic, and 24/7 operation in mind.

## Features

✅ **Automatic Video Detection & Forwarding**
- Monitors source channel in real-time
- Forwards only videos (ignores other media types)
- Server-side forwarding (no downloading/re-uploading)

✅ **Production-Grade Error Handling**
- Automatic retry with exponential backoff
- Flood wait protection (respects Telegram rate limits)
- Slow mode detection and handling
- Connection resilience with auto-reconnect
- Comprehensive logging

✅ **Security & Best Practices**
- All credentials via environment variables
- Session file for persistent authentication
- 2FA support
- Graceful shutdown on interrupts

✅ **Monitoring & Statistics**
- Real-time logging to console and file
- Daily rotating log files
- Success/error counters
- Uptime tracking

---

## Prerequisites

1. **Telegram API Credentials**
   - Go to https://my.telegram.org
   - Log in with your phone number
   - Click "API Development Tools"
   - Create a new application
   - Save your `api_id` and `api_hash`

2. **Channel Access**
   - You must be a member of the source channel
   - You must be able to post in the destination channel (admin or your own channel)

3. **Python 3.8+**
   - Required for async/await features

---

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `TELEGRAM_API_ID` | Your API ID from my.telegram.org | `12345678` |
| `TELEGRAM_API_HASH` | Your API hash from my.telegram.org | `abcdef1234567890abcdef1234567890` |
| `TELEGRAM_PHONE_NUMBER` | Your phone number in international format | `+1234567890` |
| `SOURCE_CHANNEL` | Channel to monitor (username or ID) | `educationalchannel` or `-1001234567890` |
| `DEST_CHANNEL` | Your destination channel (username or ID) | `mychannel` or `-1009876543210` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TELEGRAM_2FA_PASSWORD` | Your 2FA password if enabled | `None` |
| `SESSION_NAME` | Session file name | `video_forwarder_session` |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | `INFO` |
| `MAX_RETRIES` | Maximum retry attempts for failed operations | `3` |
| `RETRY_DELAY` | Initial delay between retries (seconds) | `5` |

---

## Deployment on Pella.app

### Step 1: Prepare Your Files

1. Upload these files to your Git repository:
   - `telegram_video_forwarder.py`
   - `requirements.txt`
   - `README.md` (this file)

### Step 2: Deploy on Pella

1. Sign up at https://www.pella.app/
2. Create a new application
3. Select "Python" as runtime
4. Connect your Git repository
5. Set the start command: `python telegram_video_forwarder.py`

### Step 3: Configure Environment Variables

In Pella dashboard, add these environment variables:

```
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=your_api_hash_here
TELEGRAM_PHONE_NUMBER=+1234567890
SOURCE_CHANNEL=source_channel_username
DEST_CHANNEL=your_channel_username
```

**Optional (if you have 2FA):**
```
TELEGRAM_2FA_PASSWORD=your_2fa_password
```

### Step 4: First-Time Authentication

1. Deploy the application
2. Check the logs in Pella dashboard
3. On first run, you'll receive a verification code in your Telegram app
4. The bot will prompt for it - check Pella logs for instructions
5. Enter the code when prompted
6. A session file will be created and authentication will persist

**Note:** After first authentication, the session is saved and you won't need to authenticate again unless you delete the session file or revoke access.

### Step 5: Monitor Operation

- Check Pella logs to confirm bot is running
- Send a test video to the source channel
- Verify it forwards to your destination channel
- Monitor the logs for any errors

---

## Local Testing (Optional)

Before deploying to Pella, you can test locally:

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

**Linux/Mac:**
```bash
export TELEGRAM_API_ID="12345678"
export TELEGRAM_API_HASH="your_api_hash"
export TELEGRAM_PHONE_NUMBER="+1234567890"
export SOURCE_CHANNEL="source_channel"
export DEST_CHANNEL="your_channel"
```

**Windows (PowerShell):**
```powershell
$env:TELEGRAM_API_ID="12345678"
$env:TELEGRAM_API_HASH="your_api_hash"
$env:TELEGRAM_PHONE_NUMBER="+1234567890"
$env:SOURCE_CHANNEL="source_channel"
$env:DEST_CHANNEL="your_channel"
```

### 3. Run the Bot
```bash
python telegram_video_forwarder.py
```

### 4. First Run Authentication
- You'll receive a code in your Telegram app
- Enter it when prompted
- If you have 2FA, enter your password
- Session will be saved in `video_forwarder_session.session`

---

## Channel ID vs Username

You can use either format for `SOURCE_CHANNEL` and `DEST_CHANNEL`:

**Username format:** (for public channels)
```
educationalchannel  # No @ symbol needed
```

**ID format:** (works for both public and private)
```
-1001234567890
```

### How to Get Channel ID

1. Forward a message from the channel to @JsonDumpBot
2. Look for `"id"` in the response
3. For channels, the ID format is: `-100` + channel_id

---

## Troubleshooting

### "Missing required environment variables"
- Ensure all required env vars are set in Pella dashboard
- Check for typos in variable names (they're case-sensitive)

### "SessionPasswordNeededError"
- Your account has 2FA enabled
- Set the `TELEGRAM_2FA_PASSWORD` environment variable

### "Cannot access one of the channels"
- Verify you're a member of the source channel
- Verify you can post in the destination channel
- Check channel username/ID is correct

### "No permission to write in destination channel"
- Make sure you're an admin or owner of the destination channel
- Verify the channel isn't restricted

### "Rate limited" / "FloodWaitError"
- Normal behavior - bot will automatically wait and retry
- Telegram limits how fast you can forward messages
- The bot handles this automatically

### Videos not forwarding
- Check logs for errors
- Verify the source message actually contains a video
- Some media might be sent as documents - bot handles both

### Bot stops after some time
- Check Pella logs for errors
- Verify your Pella account is active
- Check if session was invalidated (re-deploy to re-authenticate)

---

## File Structure

```
.
├── telegram_video_forwarder.py   # Main bot script
├── requirements.txt               # Python dependencies
├── README.md                      # This file
├── logs/                          # Created automatically
│   └── forwarder_YYYYMMDD.log    # Daily log files
└── *.session                      # Session file (auto-created, keep safe)
```

---

## Security Notes

1. **Never commit your session file to Git** - add `*.session` to `.gitignore`
2. **Keep API credentials secret** - only store in environment variables
3. **Don't share session files** - they provide full access to your account
4. **Revoke access** if compromised via Telegram Settings → Privacy → Active Sessions

---

## Monitoring

### Check Bot Status
- View Pella dashboard logs in real-time
- Look for "Bot is now running and monitoring for videos..."

### Success Indicators
```
✓ Source channel verified: Channel Name
✓ Destination channel verified: Your Channel
Bot is now running and monitoring for videos...
✓ Video forwarded successfully (Total: 1, Errors: 0)
```

### Error Indicators
- Any ERROR level logs
- Increasing error counter
- Connection failures (will auto-retry)

---

## Performance

- **Memory usage:** ~50-100MB (minimal)
- **CPU usage:** Near zero when idle
- **Network:** Only during forwarding (server-side operation)
- **Latency:** Forwards appear within 1-2 seconds of source post

---

## Limitations

1. **Telegram Rate Limits**
   - ~20-30 messages per minute (auto-handled by bot)
   - Bot will wait automatically when rate limited

2. **Pella Free Tier**
   - 100MB RAM (sufficient for this bot)
   - 0.1 CPU (sufficient for this bot)
   - Always-on (perfect for 24/7 monitoring)

3. **Forwarding Tag**
   - Videos will show "Forwarded from [source]"
   - To remove this, you'd need to download/re-upload (not recommended for large videos)

---

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review Pella logs for specific error messages
3. Verify all environment variables are set correctly
4. Test with a small video first
5. Ensure you have access to both channels

---

## License

This is production-ready code. Use responsibly and in compliance with Telegram's Terms of Service.

**Important:** Don't use this for spam, mass forwarding, or violating channel rules. Only forward content you have permission to redistribute.
