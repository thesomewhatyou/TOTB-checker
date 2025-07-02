import discord
from discord.ext import commands, tasks
import asyncio
import aiohttp
from datetime import datetime, timezone, time as dt_time, timedelta
import logging

# Project imports
try:
    from config import (DISCORD_BOT_TOKEN, DISCORD_CHANNEL_ID, PING_ROLE_ID,
                        PING_USER_IDS, LOG_LEVEL) # LOG_LEVEL is used by utils
    from utils import setup_logging
    from scraper import DailyTwistedScraper
except ImportError as e:
    print(f"Failed to import necessary modules. Ensure config.py, utils.py, and scraper.py are present and correct: {e}")
    # Attempt to set up basic logging if utils fails to load config
    try:
        import logging as lg
        lg.basicConfig(level="ERROR", format="%(asctime)s - %(levelname)s - %(message)s")
        lg.error("CRITICAL: Failed to import project modules. Bot cannot start.")
    except:
        pass # If even basic logging fails, just print
    exit(1)


# Setup logging first
setup_logging()
logger = logging.getLogger(__name__)

# --- Bot Class ---
class DandyWorldBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        intents = discord.Intents.default()
        # No special intents needed for just sending messages based on external events
        super().__init__(command_prefix=commands.when_mentioned_or("!dandy "), *args, intents=intents, **kwargs)

        self.http_session = None # Will be initialized in setup_hook
        self.scraper = None      # Will be initialized in setup_hook

        self.last_known_twisted_character = None
        self.last_known_timer_info = None # To detect timer resets even if char is same
        self.last_check_successful = True # To avoid spamming errors if wiki is down

    async def setup_hook(self):
        """
        Called when the bot is setting up.
        Initialize aiohttp.ClientSession here.
        """
        self.http_session = aiohttp.ClientSession()
        self.scraper = DailyTwistedScraper(self.http_session)
        logger.info("aiohttp.ClientSession and DailyTwistedScraper initialized.")

        # Start the background task
        self.check_twisted_board_loop.start()

    async def on_ready(self):
        logger.info(f"Bot logged in as {self.user.name} (ID: {self.user.id})")
        logger.info("Discord.py version: %s", discord.__version__)
        logger.info("Bot is ready - waiting for the next hour to start checks.")

        # Sync commands if any (not strictly necessary for this bot type but good practice)
        # try:
        #     synced = await self.tree.sync()
        #     logger.info(f"Synced {len(synced)} application commands.")
        # except Exception as e:
        #     logger.error(f"Failed to sync application commands: {e}")


    async def close(self):
        """Called when the bot is shutting down."""
        if self.http_session:
            await self.http_session.close()
            logger.info("aiohttp.ClientSession closed.")
        await super().close()

    def _get_next_run_time(self) -> datetime:
        """Calculates the next run time, which is the start of the next hour."""
        now = datetime.now(timezone.utc)
        next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        return next_hour

    @tasks.loop(seconds=1) # Check every second if it's time to run the main task
    async def check_twisted_board_loop(self):
        """
        Loop that determines when to run the hourly check.
        This approach allows for more precise timing "on the hour".
        """
        await self.wait_until_ready() # Ensure bot is connected

        now = datetime.now(timezone.utc)

        # Target: Exactly on the hour. Example: 17:00:00, 18:00:00
        if now.minute == 0 and now.second == 0:
            # Special handling for 8 PM EST / 00:00 UTC (or 01:00 UTC during EDT)
            # README specifies "midnight UTC" for 8 PM EST.
            # EDT is UTC-4, EST is UTC-5. "8 PM EST" is 1:00 AM UTC.
            # "midnight UTC" is 8 PM EDT or 7 PM EST.
            # Given "8 PM EST" and "midnight UTC" are mentioned, there's ambiguity.
            # The README also says "waits an additional minute after midnight UTC".
            # Let's assume the "midnight UTC" (00:00 UTC) check needs the delay.
            if now.hour == 0: # 00:00 UTC
                logger.info("It's 00:00 UTC (potential 8 PM US Eastern update time). Waiting 1 minute for board update.")
                await asyncio.sleep(60) # Wait 1 minute

            logger.info(f"Hourly check triggered at {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            await self.perform_twisted_check()
            # Sleep a bit to ensure we don't run this multiple times if the second ticks over slightly
            await asyncio.sleep(1.5)


    async def perform_twisted_check(self):
        """Performs the actual check of the Twisted Board."""
        logger.info("Checking Daily Twisted Board for updates...")
        if not self.scraper:
            logger.error("Scraper not initialized. Cannot perform check.")
            return

        try:
            twisted_info = await self.scraper.get_current_twisted_info()
            if not twisted_info:
                if self.last_check_successful: # Log error only on first failure
                    logger.error("Failed to get current twisted info from scraper.")
                self.last_check_successful = False
                return

            self.last_check_successful = True # Reset on successful fetch

            current_char_name = twisted_info.get("name", "Unknown")
            current_timer_info = twisted_info.get("timer_info", "Timer information not found.")
            image_url = twisted_info.get("image_url")
            wiki_page_url = twisted_info.get("wiki_page_url") or self.scraper.DAILY_TWISTED_BOARD_URL

            # Determine if an announcement is needed
            # Reason 1: Character changed
            char_changed = current_char_name != "Unknown" and self.last_known_twisted_character != current_char_name
            # Reason 2: Timer reset (even if character is the same, e.g. after a server restart or if the same char stays for another cycle)
            # This is a bit heuristic. If the timer info changes significantly, consider it a reset.
            # Or, if the character is "Unknown" and it becomes known (first run or after error).
            timer_reset_detected = (self.last_known_timer_info != current_timer_info and current_char_name != "Unknown") or \
                                   (self.last_known_twisted_character == "Unknown" and current_char_name != "Unknown")


            announcement_reason = None
            if char_changed:
                announcement_reason = f"Twisted character changed from **{self.last_known_twisted_character or 'Unknown'}** to **{current_char_name}**."
                logger.info(f"Twisted character changed: {self.last_known_twisted_character} -> {current_char_name}")
            elif timer_reset_detected and self.last_known_twisted_character == current_char_name: # Char same, but timer implies reset
                announcement_reason = f"Twisted board timer reset. Current character remains **{current_char_name}**."
                logger.info("Twisted board timer reset detected.")
            elif self.last_known_twisted_character is None and current_char_name != "Unknown": # First successful check
                 announcement_reason = f"Initial check: Current Twisted character is **{current_char_name}**."
                 logger.info(f"Initial check, twisted character: {current_char_name}")


            if announcement_reason:
                await self.send_twisted_announcement(current_char_name, image_url, wiki_page_url, twisted_info.get("timer_info"), announcement_reason)
                self.last_known_twisted_character = current_char_name
                self.last_known_timer_info = current_timer_info
            else:
                logger.info(f"No change detected. Current character: {current_char_name}. Timer: {current_timer_info}")
                # Still update if the character was previously unknown and now is known, even if no announcement (e.g. after error recovery)
                if self.last_known_twisted_character == "Unknown" and current_char_name != "Unknown":
                    self.last_known_twisted_character = current_char_name
                    self.last_known_timer_info = current_timer_info
                elif current_char_name != "Unknown" and self.last_known_twisted_character is None: # Very first run
                    self.last_known_twisted_character = current_char_name
                    self.last_known_timer_info = current_timer_info


        except Exception as e:
            logger.error(f"Error during twisted board check: {e}", exc_info=True)
            self.last_check_successful = False


    async def send_twisted_announcement(self, char_name, image_url, wiki_url, timer_info, reason):
        """Sends an announcement embed to the configured Discord channel."""
        channel = self.get_channel(DISCORD_CHANNEL_ID)
        if not channel:
            logger.error(f"Cannot find channel with ID {DISCORD_CHANNEL_ID}. Announcement not sent.")
            return

        embed = discord.Embed(
            title="🚨 Daily Twisted Board Update 🚨",
            description=reason,
            color=discord.Color.blue(), # Or a more thematic color
            url=wiki_url  # Link title to wiki page
        )
        embed.add_field(name="Current Twisted", value=char_name, inline=False)
        if timer_info:
            embed.add_field(name="Timer Information", value=timer_info, inline=False)

        if image_url:
            embed.set_image(url=image_url)
            logger.info(f"Added image to embed: {image_url}")
        else:
            logger.warning(f"No image URL available for {char_name} to include in embed.")

        embed.set_footer(text=f"Source: Dandy's World Wiki | Last Checked: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')}")

        # Construct ping message
        ping_message_parts = []
        if PING_ROLE_ID:
            ping_message_parts.append(f"<@&{PING_ROLE_ID}>")
        if PING_USER_IDS:
            for user_id in PING_USER_IDS:
                ping_message_parts.append(f"<@{user_id}>")

        ping_content = " ".join(ping_message_parts) if ping_message_parts else None

        try:
            await channel.send(content=ping_content, embed=embed)
            logger.info(f"Sent Twisted announcement to channel {DISCORD_CHANNEL_ID} for character: {char_name}")
        except discord.Forbidden:
            logger.error(f"Bot does not have permission to send messages in channel {DISCORD_CHANNEL_ID}.")
        except discord.HTTPException as e:
            logger.error(f"Failed to send message to channel {DISCORD_CHANNEL_ID}: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred while sending announcement: {e}", exc_info=True)


    @check_twisted_board_loop.before_loop
    async def before_hourly_check(self):
        """Ensures the bot is ready before the loop starts."""
        await self.wait_until_ready()
        logger.info("Hourly check loop is starting.")

# --- Main Execution ---
if __name__ == "__main__":
    if not DISCORD_BOT_TOKEN or not DISCORD_CHANNEL_ID:
        logger.critical("DISCORD_BOT_TOKEN or DISCORD_CHANNEL_ID not found in environment variables. Bot cannot start.")
        exit(1)

    bot = DandyWorldBot()

    try:
        logger.info("Starting Dandy's World Bot...")
        bot.run(DISCORD_BOT_TOKEN, log_handler=None) # Use our custom logging
    except discord.LoginFailure:
        logger.critical("Failed to log in. Check your DISCORD_BOT_TOKEN.")
    except Exception as e:
        logger.critical(f"An error occurred while trying to run the bot: {e}", exc_info=True)
    finally:
        # Ensure aiohttp session is closed if bot.run() exits unexpectedly
        # Note: bot.close() should handle this, but as a safeguard:
        if bot.http_session and not bot.http_session.closed:
            asyncio.run(bot.http_session.close()) # This might need to be run in the bot's event loop
            logger.info("Ensured aiohttp session is closed on exit.")
