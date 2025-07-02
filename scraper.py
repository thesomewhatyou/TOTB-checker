import asyncio
import aiohttp
from bs4 import BeautifulSoup, NavigableString, Tag
import re
import logging
from urllib.parse import urljoin, unquote

logger = logging.getLogger(__name__)

class DailyTwistedScraper:
    """
    Scrapes the Dandy's World wiki for Daily Twisted Board information.
    """
    BASE_WIKI_URL = "https://dandys-world-robloxhorror.fandom.com"
    DAILY_TWISTED_BOARD_URL = f"{BASE_WIKI_URL}/wiki/Daily_Twisted_Board"

    def __init__(self, session: aiohttp.ClientSession):
        self.session = session

    async def _fetch_url(self, url: str) -> str | None:
        """Fetches content from a given URL."""
        try:
            async with self.session.get(url) as response:
                response.raise_for_status()  # Raise an exception for HTTP errors
                logger.debug(f"Successfully fetched URL: {url} (status: {response.status})")
                return await response.text()
        except aiohttp.ClientError as e:
            logger.error(f"Error fetching URL {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching URL {url}: {e}")
            return None

    def _find_next_sibling_tag(self, start_tag: Tag, target_tag_name: str) -> Tag | None:
        """Finds the next sibling of a specific tag type."""
        sibling = start_tag.next_sibling
        while sibling:
            if isinstance(sibling, Tag) and sibling.name == target_tag_name:
                return sibling
            sibling = sibling.next_sibling
        return None

    async def get_current_twisted_info(self) -> dict | None:
        """
        Fetches and parses the Daily Twisted Board page to find the current
        twisted character, their image, and timer information.

        Returns:
            A dictionary with 'name', 'image_url', 'wiki_page_url', 'timer_info'
            or None if information cannot be retrieved.
        """
        html_content = await self._fetch_url(self.DAILY_TWISTED_BOARD_URL)
        if not html_content:
            return None

        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            content_div = soup.find('div', class_='mw-parser-output') # Main content area in Fandom wikis
            if not content_div:
                logger.error("Could not find main content div ('mw-parser-output') on the wiki page.")
                return None

            # --- 1. Find the Twisted Character Name and Wiki Page URL ---
            twisted_name_text = None
            twisted_char_name = "Unknown"
            twisted_char_wiki_page_url = None

            # The key phrase to find the character name
            start_phrase = "Currently, the board is occupied by "

            # Search for the phrase in all text nodes within the content_div
            # We look for a <b> tag right after the phrase.
            start_text_node = content_div.find(string=lambda text: isinstance(text, NavigableString) and start_phrase in text)

            if start_text_node:
                # The character name is often in a bold tag (<b>) which is a sibling of the text node's parent,
                # or a child of a sibling paragraph.
                # Let's try to find the <b> tag more reliably.
                # The structure is often <p>Some text <b>Character Name</b>.</p>
                # or the start_phrase is followed by an <a> tag which contains a <b> tag or is the link itself.

                current_element = start_text_node.parent
                found_char_tag = None

                # Search within the current_element and its next siblings
                for _ in range(5): # Limit search depth
                    if not current_element: break

                    # Check if the character link/name is directly after the phrase in the same element
                    if isinstance(current_element, Tag):
                        # Check children of current_element that appear after start_text_node
                        potential_char_links = []
                        # Iterate through siblings of start_text_node within its parent
                        sibling = start_text_node.next_sibling
                        while sibling:
                            if isinstance(sibling, Tag):
                                if sibling.name == 'a' or sibling.find('a'):
                                    potential_char_links.append(sibling.find('a') if sibling.find('a') else sibling)
                                elif sibling.name == 'b': # Sometimes it's just bold text not a link
                                     potential_char_links.append(sibling)
                            sibling = sibling.next_sibling

                        if not potential_char_links and hasattr(start_text_node, 'parent') and start_text_node.parent.name == 'p':
                             # Case: <p>Currently, the board is occupied by <a href="..."><b>Character</b></a>.</p>
                             # The start_text_node is the text itself. Its parent is <p>.
                             # We need to search siblings of start_text_node *within* the <p>
                             for child_node in start_text_node.parent.children:
                                 if child_node == start_text_node: continue # Skip the text node itself
                                 if isinstance(child_node, Tag):
                                     if child_node.name == 'a':
                                         potential_char_links.append(child_node)
                                         break
                                     elif child_node.name == 'b': # Direct bold tag
                                         potential_char_links.append(child_node)
                                         break
                                     # Check for <a> inside <b> or vice-versa
                                     a_in_b = child_node.find('a')
                                     if a_in_b:
                                         potential_char_links.append(a_in_b)
                                         break
                                     b_in_a = child_node.find('b') # Should be covered by 'a' case if 'a' is outer
                                     if b_in_a and child_node.name == 'a': # <a><b>Text</b></a>
                                         potential_char_links.append(child_node)
                                         break


                        if potential_char_links:
                            # Prioritize links that are not "Twisted" itself
                            best_link = None
                            for link_tag in potential_char_links:
                                link_text = link_tag.get_text(strip=True)
                                if link_text.lower() != "twisted" and link_text: # Ensure not empty
                                    best_link = link_tag
                                    break
                            if best_link:
                                found_char_tag = best_link
                                break

                    if not found_char_tag: # If not found as a sibling of the text node, move to parent's siblings
                        current_element = current_element.next_sibling
                        while current_element and not isinstance(current_element, Tag):
                            current_element = current_element.next_sibling


                if found_char_tag:
                    if found_char_tag.name == 'a':
                        twisted_char_name = found_char_tag.get_text(strip=True)
                        href = found_char_tag.get('href')
                        if href and not href.startswith('http'):
                            twisted_char_wiki_page_url = urljoin(self.BASE_WIKI_URL, href)
                        elif href:
                            twisted_char_wiki_page_url = href
                    elif found_char_tag.name == 'b': # If it was just a bold tag
                        twisted_char_name = found_char_tag.get_text(strip=True)
                        # Try to find a link for this character nearby if not directly linked
                        # This is a fallback, might not always work.
                        parent_p = found_char_tag.find_parent('p')
                        if parent_p:
                            char_link_attempt = parent_p.find('a', string=re.compile(re.escape(twisted_char_name), re.I))
                            if char_link_attempt and char_link_attempt.get('href'):
                                href = char_link_attempt.get('href')
                                if href and not href.startswith('http'):
                                    twisted_char_wiki_page_url = urljoin(self.BASE_WIKI_URL, href)
                                elif href:
                                    twisted_char_wiki_page_url = href

                    # Clean up name if it contains extra words like " (Character)"
                    twisted_char_name = re.sub(r'\s*\(.*\)\s*$', '', twisted_char_name).strip()
                    logger.info(f"Found twisted character: {twisted_char_name}")
                    if twisted_char_wiki_page_url:
                         logger.info(f"Character wiki page: {twisted_char_wiki_page_url}")

                else:
                    logger.warning("Could not find the twisted character's name tag after the introductory phrase.")
            else:
                logger.warning(f"Could not find the phrase '{start_phrase}' in the page content.")


            # --- 2. Find the Character Image ---
            # Priority:
            #   a. Image on the Daily Twisted Board page itself (often in an infobox or gallery near the top).
            #   b. If a character page URL was found, fetch that page and get the main character image.
            twisted_char_image_url = None

            # Try finding image on the main board page first (e.g. from a gallery or infobox)
            # Look for images that might be associated with the character name
            if content_div:
                # Look for <figure> elements, common for images with captions
                figures = content_div.find_all('figure', class_=re.compile(r'pi-item|image'))
                for fig in figures:
                    img_tag = fig.find('img')
                    caption_tag = fig.find('figcaption')
                    if img_tag and img_tag.get('src'):
                        # Check if caption (if exists) mentions the character
                        if caption_tag and twisted_char_name.lower() in caption_tag.get_text().lower():
                            twisted_char_image_url = self._format_image_url(img_tag.get('src'))
                            break
                        # Fallback: if no caption, but it's a prominent image and we have a character name
                        elif not caption_tag and twisted_char_name != "Unknown":
                             # This is risky, could pick up unrelated images.
                             # A better check might be if the image alt text or filename contains the character name
                            alt_text = img_tag.get('alt', '').lower()
                            src_filename = unquote(img_tag.get('src', '').split('/')[-1]).lower()
                            if twisted_char_name.lower() in alt_text or twisted_char_name.lower().replace(' ','_') in src_filename:
                                twisted_char_image_url = self._format_image_url(img_tag.get('src'))
                                break

                # If not found in figure, try searching for direct img tags that might be relevant
                if not twisted_char_image_url and twisted_char_name != "Unknown":
                    all_imgs = content_div.find_all('img')
                    for img in all_imgs:
                        alt_text = img.get('alt', '').lower()
                        src_url = img.get('src', '').lower()
                        # Simplistic check, may need refinement
                        if twisted_char_name.lower() in alt_text or twisted_char_name.lower().replace(' ','_') in unquote(src_url.split('/')[-1]):
                            # Avoid very small images/icons
                            width = img.get('width')
                            height = img.get('height')
                            try:
                                if (width and int(width) > 50) or (height and int(height) > 50) or (not width and not height): # if no size, take it
                                    twisted_char_image_url = self._format_image_url(img.get('src'))
                                    break
                            except ValueError: # If width/height is not int
                                twisted_char_image_url = self._format_image_url(img.get('src'))
                                break


            if not twisted_char_image_url and twisted_char_wiki_page_url:
                logger.info(f"Attempting to fetch image from character page: {twisted_char_wiki_page_url}")
                twisted_char_image_url = await self._fetch_character_page_image(twisted_char_wiki_page_url)

            if twisted_char_image_url:
                logger.info(f"Found character image URL: {twisted_char_image_url}")
            else:
                logger.warning(f"Could not find image for {twisted_char_name} on the main page or character page.")

            # --- 3. Find Timer Information ---
            timer_info_text = "Timer information not found."
            # Look for text like "The board will reset in..." or "Next reset:"
            # This is highly dependent on page structure and may change often.
            timer_keywords = ["board will reset in", "next reset", "changes in", "timer:"]

            timer_element = None
            for keyword in timer_keywords:
                # Search for text containing the keyword
                found_text_node = content_div.find(string=lambda text: isinstance(text, NavigableString) and keyword.lower() in text.lower())
                if found_text_node:
                    # The actual timer info is usually in the same paragraph or a following sibling.
                    # We'll take the parent paragraph's text or a few following sentences.
                    parent_p = found_text_node.find_parent('p')
                    if parent_p:
                        timer_info_text = parent_p.get_text(separator=' ', strip=True)
                    else: # If not in a paragraph, take the text itself and maybe a few siblings
                        timer_info_text = found_text_node.strip()
                        # Try to get a bit more context if it's a short string
                        if len(timer_info_text) < 30:
                            next_sibling = found_text_node.next_sibling
                            count = 0
                            while next_sibling and count < 3: # Get next 3 text nodes/tags
                                if isinstance(next_sibling, NavigableString):
                                    timer_info_text += " " + next_sibling.strip()
                                elif isinstance(next_sibling, Tag):
                                     timer_info_text += " " + next_sibling.get_text(strip=True)
                                next_sibling = next_sibling.next_sibling
                                count +=1
                    break # Found timer info for one keyword

            if timer_info_text != "Timer information not found.":
                 # Clean up common wiki artifacts like "[edit]"
                timer_info_text = re.sub(r'\[edit\]', '', timer_info_text, flags=re.IGNORECASE).strip()
                logger.info(f"Found timer info: {timer_info_text}")


            return {
                "name": twisted_char_name,
                "image_url": twisted_char_image_url,
                "wiki_page_url": twisted_char_wiki_page_url,
                "timer_info": timer_info_text
            }

        except Exception as e:
            logger.error(f"Error parsing Daily Twisted Board HTML: {e}", exc_info=True)
            return None

    def _format_image_url(self, url: str | None) -> str | None:
        """
        Formats a Fandom image URL to get a direct link to a reasonably sized image.
        Removes scaling parameters or ensures it's a direct image link.
        Example: https://static.wikia.nocookie.net/dandys-world-robloxhorror/images/a/ab/Twisted_Dandy.png/revision/latest/scale-to-width-down/150?cb=20230616000341
        Should become: https://static.wikia.nocookie.net/dandys-world-robloxhorror/images/a/ab/Twisted_Dandy.png
        """
        if not url:
            return None

        # If the URL is already a direct image path (ends with .png, .jpg, etc.) without /revision/
        if re.search(r'\.(png|jpe?g|gif|webp)$', url.lower()) and '/revision/' not in url:
            if not url.startswith('http'):
                return urljoin(self.BASE_WIKI_URL, url) # Handle relative URLs if any
            return url

        # Common Fandom image URL pattern
        match = re.match(r'(https?://static\.wikia\.nocookie\.net/.+?/images/[a-f0-9]/[a-f0-9]{2}/[^/]+\.(png|jpe?g|gif|webp)).*', url, re.IGNORECASE)
        if match:
            return match.group(1)

        # If it's a relative URL from the wiki
        if url.startswith('/images/'):
            return urljoin(self.BASE_WIKI_URL, url)

        # Fallback for other partial URLs if they contain /revision/
        if '/revision/' in url:
            url = url.split('/revision/')[0]
            if not url.startswith('http'): # If it became relative after split
                 return urljoin(self.BASE_WIKI_URL, url if url.startswith('/') else '/' + url)
            return url

        # If it's a full URL but not from static.wikia.nocookie.net, return as is if it looks like an image
        if url.startswith('http') and re.search(r'\.(png|jpe?g|gif|webp)$', url.lower()):
            return url

        logger.warning(f"Could not format image URL: {url}. Returning as is or None.")
        return url # Return original if no specific formatting rule applied but it might be valid

    async def _fetch_character_page_image(self, character_page_url: str) -> str | None:
        """
        Fetches the character's dedicated wiki page and extracts the main image URL
        (typically from an infobox).
        """
        if not character_page_url:
            return None

        html_content = await self._fetch_url(character_page_url)
        if not html_content:
            return None

        try:
            soup = BeautifulSoup(html_content, 'html.parser')

            # Look for image in the portable infobox (common on Fandom)
            infobox = soup.find('aside', class_=re.compile(r'portable-infobox'))
            if infobox:
                image_tag = infobox.find('img')
                if image_tag and image_tag.get('src'):
                    formatted_url = self._format_image_url(image_tag.get('src'))
                    if formatted_url:
                        logger.debug(f"Found image in infobox on character page: {formatted_url}")
                        return formatted_url

            # Fallback: Look for any prominent image if infobox fails or doesn't have one
            # This is less reliable
            content_div = soup.find('div', class_='mw-parser-output')
            if content_div:
                # Try to find a <figure> tag which often contains the primary image
                figure_tag = content_div.find('figure', class_=re.compile(r'pi-item|image'))
                if figure_tag:
                    img_tag = figure_tag.find('img')
                    if img_tag and img_tag.get('src'):
                        formatted_url = self._format_image_url(img_tag.get('src'))
                        logger.debug(f"Found image in <figure> on character page: {formatted_url}")
                        return formatted_url

                # Last resort: any large image in the main content not already an icon
                all_imgs = content_div.find_all('img')
                for img in all_imgs:
                    src = img.get('src')
                    if not src: continue

                    # Avoid icons or very small images
                    width = img.get('width')
                    height = img.get('height')
                    try:
                        if width and int(width) < 50: continue
                        if height and int(height) < 50: continue
                    except ValueError: # If width/height isn't a number
                        pass

                    # Check if 'thumb', 'logo', 'icon' is in the src, trying to avoid these
                    if any(keyword in src.lower() for keyword in ['thumb', 'logo', 'icon', 'badge', 'button']):
                        if 'scale-to-width-down' in src and (not width or int(width) > 100): # Fandom thumbnails can be large
                            pass # Allow if it's a scaled image that's still reasonably large
                        else:
                            continue


                    formatted_url = self._format_image_url(src)
                    if formatted_url:
                        logger.debug(f"Found general image on character page as fallback: {formatted_url}")
                        return formatted_url # Take the first reasonably large one

            logger.warning(f"Could not find a suitable character image on page: {character_page_url}")
            return None
        except Exception as e:
            logger.error(f"Error parsing character page {character_page_url} for image: {e}", exc_info=True)
            return None

async def main_test():
    """For testing the scraper independently."""
    # This requires utils.py and config.py to be in place for logging
    from utils import setup_logging
    setup_logging() # Initialize logging

    async with aiohttp.ClientSession() as session:
        scraper = DailyTwistedScraper(session)

        print("Fetching Daily Twisted Board info...")
        info = await scraper.get_current_twisted_info()

        if info:
            print("\n--- Fetched Info ---")
            print(f"Character Name: {info['name']}")
            print(f"Image URL: {info['image_url']}")
            print(f"Wiki Page URL: {info['wiki_page_url']}")
            print(f"Timer Info: {info['timer_info']}")
            print("--------------------")

            if info['name'] != "Unknown" and not info['image_url']:
                print("\nAttempting to fetch image directly from character page (if URL available)...")
                if info['wiki_page_url']:
                    image_from_char_page = await scraper._fetch_character_page_image(info['wiki_page_url'])
                    if image_from_char_page:
                        print(f"Image from character page: {image_from_char_page}")
                    else:
                        print("Still could not find image on character page.")
                else:
                    print("No character page URL to fetch image from.")
        else:
            print("Failed to retrieve twisted board information.")

if __name__ == "__main__":
    # Setup asyncio event loop for independent execution
    try:
        asyncio.run(main_test())
    except KeyboardInterrupt:
        print("Scraper test interrupted.")
    except RuntimeError as e: # Handle cases where event loop is already running (e.g. in some IDEs)
        if "cannot be called when another loop is running" in str(e):
            loop = asyncio.get_event_loop()
            loop.run_until_complete(main_test())
        else:
            raise
