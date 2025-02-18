import re
from urllib.parse import urlparse
from typing import Optional

def validate_instagram_url(url: str) -> bool:
    """
    Validate if the URL is a valid Instagram post URL.
    
    Args:
        url (str): The URL to validate

    Returns:
        bool: True if valid, False otherwise
    """
    if not url:
        return False

    try:
        # Parse URL
        parsed = urlparse(url)
        
        # Check domain
        if not any(domain in parsed.netloc.lower() 
                  for domain in ['instagram.com', 'instagr.am']):
            return False

        # Valid patterns for Instagram posts
        patterns = [
            r'^/p/[\w-]+/?$',  # Regular posts
            r'^/reel/[\w-]+/?$',  # Reels
            r'^/tv/[\w-]+/?$',  # IGTV
        ]

        # Check if path matches any valid pattern
        return any(re.match(pattern, parsed.path) for pattern in patterns)

    except Exception:
        return False

def extract_media_id(url: str) -> Optional[str]:
    """
    Extract media ID from Instagram URL.
    
    Args:
        url (str): Instagram URL

    Returns:
        Optional[str]: Media ID if found, None otherwise
    """
    if not url:
        return None

    try:
        # Extract ID from URL path
        match = re.search(r'/(?:p|reel|tv)/([\w-]+)', url)
        return match.group(1) if match else None

    except Exception:
        return None