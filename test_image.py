#!/usr/bin/env python3

import asyncio
import discord
from scraper import DailyTwistedScraper
from config import Config
from utils import setup_logging
import logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

async def test_goob_image():
    """Test function to send Twisted Goob image"""
    
    # Create scraper instance
    scraper = DailyTwistedScraper()
    config = Config()
    
    try:
        # Get a sample page and test image extraction for Twisted Vee
        html_content = await scraper.fetch_page_content()
        if html_content:
            # Test image extraction for Twisted Vee
            image_url = scraper.parse_twisted_image_url(html_content, "Twisted Goob")
            
            if image_url:
                logger.info(f"Found Twisted Vee image: {image_url}")
                
                # Create Discord bot client
                intents = discord.Intents.default()
                client = discord.Client(intents=intents)
                
                @client.event
                async def on_ready():
                    logger.info(f"Test bot connected as {client.user}")
                    
                    # Get the channel
                    channel_id = config.get_channel_id()
                    channel = client.get_channel(channel_id)
                    
                    if channel:
                        # Create embed with Twisted Vee image
                        embed = discord.Embed(
                            title="Uh Oh! Here comes Goob.",
                            description="Ouch.",
                            color=0xFF6B6B
                        )
                        
                        embed.add_field(
                            name="Image", 
                            value="Twisted Good", 
                            inline=False
                        )
                        
                        embed.set_image(url=image_url)
                        embed.set_footer(text="u are all dead")
                        
                        await channel.send(embed=embed)
                        logger.info("Test image sent successfully!")
                    else:
                        logger.error("Could not find channel")
                    
                    await client.close()
                
                # Run the bot
                token = config.discord_token
                await client.start(token)
            else:
                logger.error("Could not find Twisted Vee image")
        else:
            logger.error("Could not fetch wiki page")
            
    except Exception as e:
        logger.error(f"Error in test: {e}")
    finally:
        await scraper.close()

if __name__ == "__main__":
    asyncio.run(test_goob_image())