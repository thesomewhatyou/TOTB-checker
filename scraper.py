import aiohttp
import asyncio
import logging
import re
from bs4 import BeautifulSoup
from typing import Optional

logger = logging.getLogger(__name__)

class DailyTwistedScraper:
    """Scraper for the Daily Twisted Board wiki page"""
    
    def __init__(self):
        self.wiki_url = "https://dandys-world-robloxhorror.fandom.com/wiki/Daily_Twisted_Board"
        self.session = None
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    'User-Agent': 'DandyWorldBot/1.0 (Discord Bot)'
                }
            )
        return self.session
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def fetch_page_content(self) -> Optional[str]:
        """Fetch the wiki page content"""
        try:
            session = await self._get_session()
            async with session.get(self.wiki_url) as response:
                if response.status == 200:
                    content = await response.text()
                    logger.debug("Successfully fetched wiki page")
                    return content
                else:
                    logger.error(f"HTTP {response.status} when fetching wiki page")
                    return None
        except asyncio.TimeoutError:
            logger.error("Timeout when fetching wiki page")
            return None
        except Exception as e:
            logger.error(f"Error fetching wiki page: {e}")
            return None
    
    def parse_current_twisted(self, html_content: str) -> Optional[str]:
        """Parse the HTML content to extract the current twisted"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for the text "Currently, the board is occupied by"
            text_content = soup.get_text()
            
            # Use regex to find the pattern
            pattern = r"Currently,\s+the\s+board\s+is\s+occupied\s+by\s+(.+?)(?:\.|$|\n)"
            match = re.search(pattern, text_content, re.IGNORECASE | re.DOTALL)
            
            if match:
                twisted_name = match.group(1).strip()
                # Clean up the name (remove extra whitespace, periods, etc.)
                twisted_name = re.sub(r'\s+', ' ', twisted_name)
                twisted_name = twisted_name.rstrip('.')
                logger.debug(f"Extracted twisted name: {twisted_name}")
                return twisted_name
            
            # Alternative method: look for the specific HTML structure
            # Find text containing "Currently, the board is occupied by"
            for element in soup.find_all(text=re.compile(r"Currently.*occupied by", re.IGNORECASE)):
                parent = element.parent
                if parent:
                    # Look for the next link or text that contains "Twisted"
                    next_elements = parent.find_next_siblings()
                    for next_elem in next_elements:
                        links = next_elem.find_all('a') if hasattr(next_elem, 'find_all') else []
                        for link in links:
                            href = link.get('href', '')
                            text = link.get_text().strip()
                            if 'Twisted' in text and '/wiki/Twisted_' in href:
                                logger.debug(f"Found twisted via HTML parsing: {text}")
                                return text
            
            # Try to find any link with "Twisted" in the title near the occupied text
            occupied_text = soup.find(text=re.compile(r"Currently.*occupied by", re.IGNORECASE))
            if occupied_text:
                # Get the parent element and search nearby
                parent = occupied_text.parent
                for i in range(3):  # Check next few elements
                    if parent.next_sibling:
                        parent = parent.next_sibling
                        if hasattr(parent, 'find'):
                            twisted_link = parent.find('a', href=re.compile(r'/wiki/Twisted_'))
                            if twisted_link:
                                twisted_name = twisted_link.get_text().strip()
                                logger.debug(f"Found twisted via sibling search: {twisted_name}")
                                return twisted_name
            
            logger.warning("Could not find current twisted in page content")
            return None
            
        except Exception as e:
            logger.error(f"Error parsing HTML content: {e}")
            return None
    
    def parse_timer_info(self, html_content: str) -> Optional[str]:
        """Parse the HTML content to extract timer information"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            text_content = soup.get_text()
            
            # Look for timer patterns like "It will be X hours, Y minutes and Z seconds until"
            timer_patterns = [
                r"It will be (.+?) until the Daily Twisted Board changes",
                r"(\d+) hours?, (\d+) minutes? and (\d+) seconds? until",
                r"(\d+) hours? and (\d+) minutes? until",
                r"(\d+) minutes? and (\d+) seconds? until",
                r"(\d+) seconds? until"
            ]
            
            for pattern in timer_patterns:
                match = re.search(pattern, text_content, re.IGNORECASE)
                if match:
                    timer_text = match.group(0).strip()
                    logger.debug(f"Extracted timer info: {timer_text}")
                    return timer_text
            
            logger.debug("No timer information found")
            return None
            
        except Exception as e:
            logger.error(f"Error parsing timer info: {e}")
            return None
    
    async def get_current_twisted(self) -> Optional[str]:
        """Get the current twisted from the wiki page"""
        try:
            html_content = await self.fetch_page_content()
            if html_content:
                return self.parse_current_twisted(html_content)
            return None
        except Exception as e:
            logger.error(f"Error getting current twisted: {e}")
            return None
    
    def parse_twisted_image_url(self, html_content: str, twisted_name: str) -> Optional[str]:
        """Parse the HTML content to extract the twisted character image URL"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove "Twisted " prefix to get the character name
            character_name = twisted_name.replace("Twisted ", "").strip()
            
            # Look for image with alt text containing the character name
            img_tags = soup.find_all('img', alt=True)
            for img in img_tags:
                alt_text = img.get('alt', '').lower()
                if character_name.lower() in alt_text and 'twisted' in alt_text:
                    src = img.get('src')
                    if src:
                        # Handle relative URLs
                        if src.startswith('//'):
                            return f"https:{src}"
                        elif src.startswith('/'):
                            return f"https://dandys-world-robloxhorror.fandom.com{src}"
                        else:
                            return src
            
            # Fallback: look for any image with the character name
            for img in img_tags:
                alt_text = img.get('alt', '').lower()
                if character_name.lower() in alt_text:
                    src = img.get('src')
                    if src:
                        if src.startswith('//'):
                            return f"https:{src}"
                        elif src.startswith('/'):
                            return f"https://dandys-world-robloxhorror.fandom.com{src}"
                        else:
                            return src
            
            logger.warning(f"Could not find image for {twisted_name}")
            return None
            
        except Exception as e:
            logger.error(f"Error parsing twisted image URL: {e}")
            return None

    async def get_twisted_and_timer_info(self) -> tuple[Optional[str], Optional[str]]:
        """Get both current twisted and timer information"""
        try:
            html_content = await self.fetch_page_content()
            if html_content:
                twisted = self.parse_current_twisted(html_content)
                timer = self.parse_timer_info(html_content)
                return twisted, timer
            return None, None
        except Exception as e:
            logger.error(f"Error getting twisted and timer info: {e}")
            return None, None
    
    async def get_twisted_info_with_image(self) -> tuple[Optional[str], Optional[str], Optional[str]]:
        """Get current twisted, timer information, and image URL"""
        try:
            html_content = await self.fetch_page_content()
            if html_content:
                twisted = self.parse_current_twisted(html_content)
                timer = self.parse_timer_info(html_content)
                image_url = None
                if twisted:
                    image_url = self.parse_twisted_image_url(html_content, twisted)
                return twisted, timer, image_url
            return None, None, None
        except Exception as e:
            logger.error(f"Error getting twisted info with image: {e}")
            return None, None, None
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        if hasattr(self, 'session') and self.session and not self.session.closed:
            # Note: This won't work in async context, but it's a fallback
            try:
                asyncio.create_task(self.session.close())
            except:
                pass
