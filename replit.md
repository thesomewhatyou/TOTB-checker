# Dandy's World Discord Bot

## Overview

This is a Discord bot that monitors the Daily Twisted Board from the Dandy's World wiki and sends notifications to Discord channels when the twisted character changes. The bot scrapes the wiki page every 30 minutes and alerts users when a new twisted character is available.

## System Architecture

The bot follows a modular, event-driven architecture:

- **Main Bot Module (`bot.py`)**: Core Discord bot logic using discord.py library
- **Configuration Management (`config.py`)**: Environment-based configuration with validation
- **Web Scraping (`scraper.py`)**: Asynchronous wiki page scraping using aiohttp and BeautifulSoup
- **Utilities (`utils.py`)**: Logging setup and helper functions for text processing

The architecture prioritizes:
- Asynchronous operations for non-blocking Discord interactions
- Modular design for easy maintenance and testing
- Robust error handling and logging
- Environment variable configuration for security

## Key Components

### Discord Bot (`DandyWorldBot`)
- Extends `discord.ext.commands.Bot`
- Implements periodic monitoring via Discord.py tasks
- Handles Discord events (on_ready, setup_hook)
- Manages state tracking for twisted character changes

### Configuration Manager (`Config`)
- Validates required environment variables
- Handles Discord channel and user ID parsing
- Provides centralized configuration access
- Implements graceful degradation for missing optional configs

### Web Scraper (`DailyTwistedScraper`)
- Asynchronous HTTP client using aiohttp
- Session management with proper cleanup
- HTML parsing with BeautifulSoup
- Timeout and error handling for network requests

### Utilities
- Centralized logging configuration with file and console output
- Text processing functions for wiki content
- Discord ID validation utilities

## Data Flow

1. **Bot Initialization**: Load configuration, create scraper instance, set up Discord connection
2. **Initial State**: Fetch current twisted character on startup
3. **Periodic Monitoring**: Every 30 minutes, scrape wiki page for updates
4. **Change Detection**: Compare new twisted character with previous state
5. **Notification**: Send Discord message with pings when change detected
6. **State Update**: Store new twisted character as current state

## External Dependencies

### Core Libraries
- `discord.py`: Discord API interaction and bot framework
- `aiohttp`: Asynchronous HTTP client for web scraping
- `beautifulsoup4`: HTML parsing for wiki content extraction
- `asyncio`: Asynchronous programming support

### External Services
- **Discord API**: Bot authentication, message sending, channel management
- **Dandy's World Wiki**: Source of Daily Twisted Board data via web scraping

### Environment Variables
- `DISCORD_BOT_TOKEN` (required): Bot authentication token
- `DISCORD_CHANNEL_ID` (optional): Target channel for notifications
- `PING_ROLE_ID` (optional): Role to ping on updates
- `PING_USER_IDS` (optional): Comma-separated user IDs to ping
- `LOG_LEVEL` (optional): Logging verbosity level

## Deployment Strategy

The application is designed for containerized deployment:

### Environment Setup
- Python 3.8+ runtime environment
- Environment variables for configuration
- Persistent logging directory (`logs/`)

### Scalability Considerations
- Single-instance deployment (state stored in memory)
- Stateless design allows for easy restarts
- Configurable monitoring intervals
- Session management prevents resource leaks

### Monitoring
- File-based logging with daily rotation
- Structured log format for debugging
- Health checks via Discord connection status
- Error handling prevents bot crashes

## Changelog
- July 01, 2025. Initial setup
- July 01, 2025. Removed duplicate announcement prevention - bot now announces every check regardless of whether the twisted character is the same as before
- July 01, 2025. Added smart change detection - bot now only announces when twisted actually changes OR when timer resets with same twisted (indicating new daily cycle)
- July 01, 2025. Added timer information parsing to detect when daily board resets
- July 01, 2025. Updated announcement logic to be more intelligent about when to notify users
- July 01, 2025. Added hardcoded environment variables for private deployment (DISCORD_CHANNEL_ID: 1381153101414924409, PING_ROLE_ID: 1381148457212841985)
- July 01, 2025. Changed monitoring schedule from every 30 minutes to every hour on the exact hour, with time synchronization to eliminate delays
- July 01, 2025. Added special 1-minute delay for 8 PM EST (midnight UTC) checks to account for board update timing
- July 02, 2025. Added image attachment functionality - bot now extracts and displays Twisted character images from the wiki in Discord announcements

## User Preferences

Preferred communication style: Simple, everyday language.
Daily Twisted Board updates at 8PM EST: Bot should continue checking but only announce when there's an actual change or when the timer resets with the same twisted (indicating a new daily cycle).
Monitor timer information: Bot should parse timer data from the wiki to detect when the board resets.
Smart notifications: Always check the board, but only send Discord announcements when there's a meaningful change - either a new twisted character or a timer reset with the same character.