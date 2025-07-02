import asyncio
import aiohttp
import logging

# Attempt to import project modules
try:
    from scraper import DailyTwistedScraper
    from utils import setup_logging # To initialize logging similar to the bot
    # We don't need config directly here, but utils might use it.
except ImportError as e:
    print(f"Error importing project modules (scraper, utils): {e}")
    print("Please ensure these files are in the same directory or accessible in PYTHONPATH.")
    print("For basic testing without full logging, these imports might not be critical if stubbed.")
    # Fallback basic logging if utils can't be imported
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    # Define a dummy DailyTwistedScraper if import fails, so the script can be partially reviewed
    if 'DailyTwistedScraper' not in globals():
        class DailyTwistedScraper:
            def __init__(self, session): self.session = session; logging.warning("Using dummy Scraper class.")
            async def get_current_twisted_info(self): logging.error("Dummy scraper cannot fetch info."); return None
            async def _fetch_character_page_image(self, url): logging.error("Dummy scraper cannot fetch image."); return None

logger = logging.getLogger(__name__)

async def run_image_test():
    """
    Tests the image extraction functionality of the DailyTwistedScraper.
    It will:
    1. Fetch the main Daily Twisted Board page.
    2. Try to extract the character name and image URL from it.
    3. If an image URL is found directly, print it.
    4. If a character-specific wiki page URL is found but no direct image,
       it will then try to fetch and extract the image from that character page.
    """
    if 'setup_logging' in globals():
        setup_logging() # Initialize logging from utils
        logger.info("Initialized logging for image test.")
    else:
        logger.info("Basic logging configured for image test (utils.setup_logging not found).")

    async with aiohttp.ClientSession() as session:
        scraper = DailyTwistedScraper(session)

        logger.info("--- Starting Image Extraction Test ---")
        logger.info(f"Attempting to fetch info from: {scraper.DAILY_TWISTED_BOARD_URL}")

        twisted_info = await scraper.get_current_twisted_info()

        if not twisted_info:
            logger.error("Failed to retrieve any information from the Daily Twisted Board page.")
            return

        character_name = twisted_info.get("name", "Unknown Character")
        image_url_from_main_page = twisted_info.get("image_url")
        character_wiki_page_url = twisted_info.get("wiki_page_url")

        logger.info(f"Character Name Extracted: {character_name}")

        if image_url_from_main_page:
            logger.info(f"Image URL found on main board page: {image_url_from_main_page}")
        else:
            logger.info("No image URL found directly on the Daily Twisted Board page.")
            if character_wiki_page_url:
                logger.info(f"Character specific wiki page URL found: {character_wiki_page_url}")
                logger.info("Attempting to fetch image from character's page...")

                image_from_char_page = await scraper._fetch_character_page_image(character_wiki_page_url)

                if image_from_char_page:
                    logger.info(f"Image URL found on character page ({character_name}): {image_from_char_page}")
                else:
                    logger.warning(f"Could not find an image for {character_name} on their dedicated page either.")
            else:
                logger.warning(f"No character-specific wiki page URL found for {character_name}, so cannot attempt secondary image fetch.")

        logger.info("--- Image Extraction Test Complete ---")

if __name__ == "__main__":
    print("Running Dandy's World Bot Image Scraper Test...")
    print("This will fetch live data from the wiki.")

    # Setup asyncio event loop
    try:
        asyncio.run(run_image_test())
    except KeyboardInterrupt:
        print("\nImage test interrupted by user.")
    except RuntimeError as e: # Handle cases where event loop is already running
        if "cannot be called when another loop is running" in str(e):
            logger.info("Asyncio event loop already running. Using existing loop.")
            loop = asyncio.get_event_loop()
            loop.run_until_complete(run_image_test())
        else:
            logger.error(f"RuntimeError during test execution: {e}")
            raise
    except Exception as e:
        logger.error(f"An unexpected error occurred during the test: {e}", exc_info=True)
