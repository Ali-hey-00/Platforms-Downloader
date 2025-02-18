import json
import re
import aiohttp
import logging
from typing import Dict, Optional, List
from bs4 import BeautifulSoup
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class MediaExtractor:
    """Extract media information from Instagram posts without login."""
    
    def __init__(self):
        self.session = aiohttp.ClientSession()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'DNT': '1',
        }

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        """Close aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()

    async def extract_media_info(self, url: str) -> Dict:
        """
        Extract media information from Instagram post.
        
        Args:
            url (str): Instagram post URL

        Returns:
            Dict: Media information including URLs and metadata
        """
        try:
            async with self.session.get(url, headers=self.headers) as response:
                if response.status != 200:
                    raise ValueError(f"Failed to fetch URL: {response.status}")

                html = await response.text()
                
                # Parse page content
                soup = BeautifulSoup(html, 'html.parser')
                
                # Try to find media data in page
                media_data = self._extract_media_data(soup)
                if not media_data:
                    raise ValueError("No media data found")

                return {
                    'type': media_data.get('type', 'image'),
                    'urls': media_data.get('urls', []),
                    'thumbnail': media_data.get('thumbnail'),
                    'caption': media_data.get('caption'),
                    'timestamp': media_data.get('timestamp')
                }

        except Exception as e:
            logger.error(f"Error extracting media info: {str(e)}")
            raise

    def _extract_media_data(self, soup: BeautifulSoup) -> Dict:
        """
        Extract media data from page content.
        
        Args:
            soup (BeautifulSoup): Parsed HTML content

        Returns:
            Dict: Extracted media data
        """
        try:
            # Find media data in page scripts
            for script in soup.find_all('script', type='application/ld+json'):
                try:
                    data = json.loads(script.string)
                    if '@type' in data and data['@type'] in ['ImageObject', 'VideoObject']:
                        return {
                            'type': 'video' if data['@type'] == 'VideoObject' else 'image',
                            'urls': [data.get('contentUrl')] if data.get('contentUrl') else [],
                            'thumbnail': data.get('thumbnailUrl'),
                            'caption': data.get('caption'),
                            'timestamp': data.get('uploadDate')
                        }
                except json.JSONDecodeError:
                    continue

            # Alternative method: Look for meta tags
            og_video = soup.find('meta', property='og:video')
            og_image = soup.find('meta', property='og:image')

            if og_video:
                return {
                    'type': 'video',
                    'urls': [og_video['content']],
                    'thumbnail': og_image['content'] if og_image else None,
                    'caption': self._extract_caption(soup),
                    'timestamp': self._extract_timestamp(soup)
                }
            elif og_image:
                return {
                    'type': 'image',
                    'urls': [og_image['content']],
                    'thumbnail': og_image['content'],
                    'caption': self._extract_caption(soup),
                    'timestamp': self._extract_timestamp(soup)
                }

        except Exception as e:
            logger.error(f"Error parsing media data: {str(e)}")
            
        return {}

    def _extract_caption(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract post caption from meta tags"""
        meta_desc = soup.find('meta', property='og:description')
        if meta_desc:
            return meta_desc['content']
        return None

    def _extract_timestamp(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract post timestamp from meta tags"""
        time_tag = soup.find('meta', property='article:published_time')
        if time_tag:
            return time_tag['content']
        return None