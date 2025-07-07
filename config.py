import os
import logging

logger = logging.getLogger(__name__)

class Config:
    """Configuration manager for the Discord bot"""
    
    def __init__(self):
        self.discord_token = os.getenv('DISCORD_BOT_TOKEN')
        self.channel_id = self._get_channel_id()
        self.ping_role_id = os.getenv('PING_ROLE_ID', '1381148457212841985')
        self.ping_user_ids = self._get_ping_user_ids()
        
        # Validate required config
        self._validate_config()
    
    def _get_channel_id(self):
        """Get and validate channel ID"""
        channel_id_str = os.getenv('DISCORD_CHANNEL_ID', '1381153101414924409')
        if not channel_id_str:
            logger.warning("DISCORD_CHANNEL_ID not set")
            return None
            
        try:
            return int(channel_id_str)
        except ValueError:
            logger.error(f"Invalid DISCORD_CHANNEL_ID: {channel_id_str}")
            return None
    
    def _get_ping_user_ids(self):
        """Get ping user IDs from environment"""
        ping_users_str = os.getenv('PING_USER_IDS', '')
        if not ping_users_str:
            return []
            
        try:
            return [int(uid.strip()) for uid in ping_users_str.split(',') if uid.strip()]
        except ValueError:
            logger.error(f"Invalid PING_USER_IDS format: {ping_users_str}")
            return []
    
    def _validate_config(self):
        """Validate required configuration"""
        if not self.discord_token:
            raise ValueError("DISCORD_BOT_TOKEN is required")
        
        if not self.channel_id:
            logger.warning("DISCORD_CHANNEL_ID not configured - bot will not send announcements")
    
    def get_channel_id(self):
        """Get the configured channel ID"""
        return self.channel_id
    
    def get_ping_mentions(self):
        """Get ping mentions string for announcements"""
        mentions = []
        
        # Add role ping if configured
        if self.ping_role_id:
            try:
                role_id = int(self.ping_role_id)
                mentions.append(f"<@&{role_id}>")
            except ValueError:
                logger.error(f"Invalid PING_ROLE_ID: {self.ping_role_id}")
        
        # Add user pings if configured
        for user_id in self.ping_user_ids:
            mentions.append(f"<@{user_id}>")
        
        return " ".join(mentions)
    
    def get_wiki_url(self):
        """Get the wiki URL to monitor"""
        return "https://dandys-world-robloxhorror.fandom.com/wiki/Daily_Twisted_Board"
