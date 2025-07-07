import discord
from discord.ext import commands, tasks
import asyncio
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from config import Config
from scraper import DailyTwistedScraper
from utils import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

class DandyWorldBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = False  # We don't need message content for this bot
        super().__init__(command_prefix='!', intents=intents)
        
        self.config = Config()
        self.scraper = DailyTwistedScraper()
        self.last_twisted = None
        self.last_timer_info = None
        
    async def setup_hook(self):
        """Called when the bot is starting up"""
        logger.info("Bot is starting up...")
        # Start the monitoring task
        self.monitor_twisted_board.start()
        
    async def on_ready(self):
        """Called when the bot has logged in"""
        logger.info(f'{self.user} has connected to Discord!')
        logger.info(f'Bot is in {len(self.guilds)} guilds')
        
        # Get initial state
        try:
            current_twisted, timer_info = await self.scraper.get_twisted_and_timer_info()
            if current_twisted:
                self.last_twisted = current_twisted
                self.last_timer_info = timer_info
                logger.info(f"Initial twisted state: {current_twisted}")
                if timer_info:
                    logger.info(f"Timer info: {timer_info}")
            else:
                logger.warning("Could not get initial twisted state")
        except Exception as e:
            logger.error(f"Error getting initial state: {e}")
    
    @tasks.loop(hours=1)
    async def monitor_twisted_board(self):
        """Monitor the Daily Twisted Board every hour on the hour"""
        try:
            # Check if it's 8 PM EST (midnight UTC) - the update time
            now = datetime.now(timezone.utc)
            if now.hour == 0 and now.minute == 0:  # Midnight UTC = 8 PM EST
                logger.info("8 PM EST (midnight UTC) detected - waiting 1 minute for board update...")
                await asyncio.sleep(60)  # Wait 1 minute for board to update
                logger.info("1 minute delay complete - now checking board...")
            
            logger.info("Checking Daily Twisted Board for updates...")
            current_twisted, timer_info, image_url = await self.scraper.get_twisted_info_with_image()
            
            if current_twisted is None:
                logger.warning("Failed to get current twisted - skipping this check")
                return
                
            logger.info(f"Current twisted: {current_twisted}")
            if timer_info:
                logger.info(f"Timer info: {timer_info}")
            
            # Check if twisted changed OR if timer restarted with same twisted
            should_announce = False
            announcement_reason = ""
            
            if self.last_twisted != current_twisted:
                # Twisted character changed
                should_announce = True
                announcement_reason = f"Twisted changed from {self.last_twisted} to {current_twisted}"
            elif self.last_twisted == current_twisted and timer_info and self.last_timer_info:
                # Same twisted but check if timer restarted (indicating new cycle)
                # If timer shows a large time (like 20+ hours), it likely restarted
                if "hours" in timer_info and any(int(h) > 20 for h in timer_info.split() if h.isdigit()):
                    should_announce = True
                    announcement_reason = f"Timer restarted with same twisted: {current_twisted}"
            
            if should_announce:
                logger.info(announcement_reason)
                await self.announce_current_twisted(current_twisted, announcement_reason, image_url)
            else:
                logger.info(f"No announcement needed - still {current_twisted}")
            
            # Update stored state
            self.last_twisted = current_twisted
            self.last_timer_info = timer_info
                
        except Exception as e:
            logger.error(f"Error in monitor_twisted_board: {e}")
    
    @monitor_twisted_board.before_loop
    async def before_monitor_twisted_board(self):
        """Wait until the bot is ready and sync to the next hour before starting the monitoring loop"""
        await self.wait_until_ready()
        
        # Calculate time until next hour
        now = datetime.now()
        next_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        wait_time = (next_hour - now).total_seconds()
        
        logger.info(f"Bot is ready - syncing to next hour in {wait_time:.1f} seconds")
        logger.info(f"Next check will be at {next_hour.strftime('%H:%M:%S')}")
        
        # Wait until the next hour
        await asyncio.sleep(wait_time)
        logger.info("Synchronized to the hour - starting monitoring loop")
    
    async def announce_current_twisted(self, current_twisted: str, reason: str = "", image_url: Optional[str] = None):
        """Announce the current twisted from the Daily Twisted Board"""
        try:
            channel_id = self.config.get_channel_id()
            if not channel_id:
                logger.error("No channel ID configured")
                return
                
            channel = self.get_channel(channel_id)
            if not channel:
                logger.error(f"Could not find channel with ID {channel_id}")
                return
            
            # Check if channel supports sending messages
            if not hasattr(channel, 'send'):
                logger.error(f"Channel {channel_id} does not support sending messages")
                return
            
            # Create embed message
            embed = discord.Embed(
                title="🎭 Daily Twisted Board Update!",
                description=f"Currently, the board is occupied by:",
                color=0xFF6B6B,
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="Current Twisted", 
                value=current_twisted, 
                inline=False
            )
            
            if reason:
                embed.add_field(
                    name="Update Reason",
                    value=reason,
                    inline=False
                )
            
            embed.add_field(
                name="📍 Source", 
                value="[Daily Twisted Board Wiki](https://dandys-world-robloxhorror.fandom.com/wiki/Daily_Twisted_Board)", 
                inline=False
            )
            
            # Add image if available
            if image_url:
                embed.set_image(url=image_url)
                logger.info(f"Added image to embed: {image_url}")
            else:
                logger.warning("No image URL available for this twisted character")
            
            embed.set_footer(text="Dandy's World Bot")
            
            # Get ping mentions
            ping_mentions = self.config.get_ping_mentions()
            message_content = f"{ping_mentions}" if ping_mentions else ""
            
            await channel.send(content=message_content, embed=embed)
            channel_name = getattr(channel, 'name', f'Channel {channel_id}')
            logger.info(f"Announced current twisted in channel {channel_name}: {current_twisted}")
            
        except Exception as e:
            logger.error(f"Error announcing current twisted: {e}")
    


async def main():
    """Main function to run the bot"""
    bot = DandyWorldBot()
    
    try:
        # Get bot token from environment
        token = os.getenv('DISCORD_BOT_TOKEN')
        if not token:
            logger.error("DISCORD_BOT_TOKEN not found in environment variables")
            return
            
        await bot.start(token)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Error running bot: {e}")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
