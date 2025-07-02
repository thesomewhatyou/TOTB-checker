# TOTB-checker
# Dandy's World Discord Bot

A Python Discord bot that monitors the Daily Twisted Board from the Dandy's World wiki and sends automated notifications to Discord channels when the twisted character changes, complete with character images.

## 🎯 Features

- **Hourly Monitoring**: Checks the Daily Twisted Board exactly on the hour
- **Smart Change Detection**: Only announces when the twisted character actually changes or when the timer resets
- **Image Integration**: Automatically extracts and displays twisted character images from the wiki
- **Perfect Timing**: Special 1-minute delay for 8 PM EST updates to account for board update timing
- **Role Pinging**: Configurable role and user mentions for announcements
- **Robust Error Handling**: Comprehensive logging and graceful failure recovery

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Discord Bot Token
- Discord Channel ID for announcements, plus a role ID (optional. Clone the repo and uncomment the section where you put the ROLE_ID)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd dandys-world-bot
   ```

2. **Install dependencies**
   ```bash
   uv add discord.py aiohttp beautifulsoup4 python-dotenv trafilatura
   ```

3. **Environment Setup**
   
   Create a `.env` file in the project root:
   ```env
   DISCORD_BOT_TOKEN=your_bot_token_here
   DISCORD_CHANNEL_ID=your_channel_id_here
   PING_ROLE_ID=your_role_id_here
   PING_USER_IDS=user1_id,user2_id,user3_id
   LOG_LEVEL=INFO
   ```

4. **Run the bot**
   ```bash
   python bot.py
   ```

## ⚙️ Configuration

### Environment Variables
BOT_TOKEN is required. 
CHANNEL_ID is required.
A ROLE_ID is optional. 

### Discord Bot Setup

1. **Create a Discord Application**
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Click "New Application" and give it a name
   - Navigate to the "Bot" section
   - Click "Add Bot" and copy the token

2. **Set Bot Permissions**
   
   Your bot needs these permissions:
   - Send Messages
   - Embed Links
   - Attach Files
   - Read Message History
   - Use External Emojis

3. **Invite Bot to Server**
   ```
   https://discord.com/api/oauth2/authorize?client_id=YOUR_BOT_CLIENT_ID&permissions=52224&scope=bot
   ```

## 📋 How It Works

### Monitoring Schedule

- **Regular Checks**: Every hour on the exact hour (17:00, 18:00, 19:00, etc.)
- **8 PM EST Special**: Waits an additional minute after midnight UTC for board updates
- **Smart Announcements**: Only sends notifications when the twisted character actually changes.

### Data Sources

- **Primary**: [Dandy's World Daily Twisted Board Wiki](https://dandys-world-robloxhorror.fandom.com/wiki/Daily_Twisted_Board)
- **Images**: Character images extracted directly from wiki pages
- **Timer Info**: Countdown information for next board update

### Announcement Format

The bot sends rich Discord embeds containing:
- Current twisted character name
- Character image from the wiki
- Update reason (character change or timer reset)
- Link to the wiki source
- Role/user pings (if configured)

## 🏗️ Project Structure

```
dandys-world-bot/
├── bot.py              # Main Discord bot logic
├── config.py           # Configuration management
├── scraper.py          # Wiki scraping functionality
├── utils.py            # Utility functions and logging
├── test_image.py       # Image functionality testing
├── .env.example        # Environment variables template
├── readme.md          # Project documentation
└── logs/              # Log files directory
```

## 🔧 Development

### Architecture

- **Asynchronous Design**: Built with `asyncio` for non-blocking operations
- **Modular Structure**: Separated concerns for easy maintenance
- **Error Resilience**: Comprehensive error handling and logging
- **Session Management**: Proper HTTP session cleanup

### Key Components

- **DandyWorldBot**: Main Discord bot class with monitoring logic
- **DailyTwistedScraper**: Web scraping for wiki content and images
- **Config**: Environment-based configuration management
- **Utilities**: Logging setup and text processing helpers

### Testing

Test the image functionality:
```bash
python test_image.py
```

### Logging

Logs are stored in the `logs/` directory with daily rotation:
- Console output for real-time monitoring
- File logging for historical analysis
- Configurable log levels

## 📊 Monitoring

### Health Checks

The bot provides several monitoring indicators:
- Discord connection status
- Wiki accessibility
- Successful twisted character detection
- Image extraction success rates

### Log Analysis

Key log events to monitor:
```
INFO - Bot is ready - syncing to next hour
INFO - Checking Daily Twisted Board for updates
INFO - Twisted changed from X to Y
INFO - Added image to embed: [URL]
ERROR - Failed to get current twisted
```

## 🚨 Troubleshooting

### Common Issues

**Bot won't start**
- Check Discord token validity
- Verify bot permissions in server
- Ensure Python dependencies are installed

**No announcements**
- Verify channel ID is correct
- Check bot has send permissions in target channel
- Monitor logs for scraping errors
- Also make sure it's actually added to the server. It's really sucky sometimes

**Images not showing**
- Wiki images may be temporarily unavailable
- Check network connectivity
- Verify image URL accessibility

**Missing timer reset detection**
- Timer parsing depends on wiki formatting
- Check if wiki page structure changed
- Monitor logs for parsing errors

### Debug Mode

Enable debug logging:
```env
LOG_LEVEL=DEBUG
```

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Code Style

- Follow PEP 8 conventions
- Use type hints where appropriate
- Include docstrings for public methods
- Add logging for important operations

## 📜 License

This project is licensed under the Unlicense License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Dandy's World](https://www.roblox.com/games/12452349149/Dandys-World) game community
- [Discord.py](https://discordpy.readthedocs.io/) library developers
- Fandom wiki contributors

## 📞 Support

For support or questions:
- Check the logs in `logs/` directory
- Review configuration in `.env` file
- Monitor Discord bot status in server
- Ask thesomewhatyou
---


TL;DR, basically this bot scrapes the [Dandy's World fandom wiki](https://dandys-world-robloxhorror.fandom.com/wiki/Daily_Twisted_Board) looking for content after the "Currently, the board is occupied by" and then pinging a role. Put all info like channel ID and role ID in the .env (this bot supports one channel and role) and basically just run the project. This requires an active internet connection. This project is open-source, but made by Jules from Google. As a tester, I am obligated to do something like this.    
*Last updated: July 2, 2025*
