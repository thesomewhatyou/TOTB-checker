import logging
import os
from datetime import datetime

def setup_logging():
    """Setup logging configuration"""
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'logs/bot_{datetime.now().strftime("%Y%m%d")}.log'),
            logging.StreamHandler()
        ]
    )
    
    # Set third-party library log levels
    logging.getLogger('discord').setLevel(logging.WARNING)
    logging.getLogger('aiohttp').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)

def format_twisted_name(name: str) -> str:
    """Format twisted name for display"""
    if not name:
        return "Unknown"
    
    # Ensure it starts with "Twisted" if it doesn't already
    if not name.startswith("Twisted"):
        name = f"Twisted {name}"
    
    return name.strip()

def validate_discord_id(id_str: str) -> bool:
    """Validate that a string is a valid Discord ID"""
    try:
        discord_id = int(id_str)
        # Discord IDs are snowflakes, typically 17-19 digits
        return 10**16 <= discord_id <= 10**19
    except (ValueError, TypeError):
        return False

def clean_wiki_text(text: str) -> str:
    """Clean text extracted from wiki"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove common wiki artifacts
    text = text.replace('[edit]', '')
    text = text.replace('[Sign in to edit]', '')
    
    return text.strip()
