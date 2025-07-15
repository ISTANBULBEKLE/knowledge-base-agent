from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import aiohttp
from typing import Dict, Optional
import asyncio
from urllib.parse import urlparse
import re

class WebScraper:
    def __init__(self):
        self.session = None
    
    async def scrape_url(self, url: str) -> Dict:
        """Main scraping method that handles different content types"""
        try:
            # Use Playwright for JavaScript-heavy sites
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                await page.goto(url, wait_until="networkidle")
                content = await page.content()
                title = await page.title()
                
                await browser.close()
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract text content
            text_content = self._extract_text(soup)
            
            # Extract metadata
            metadata = self._extract_metadata(soup, url)
            
            return {
                "url": url,
                "title": title or metadata.get("title", ""),
                "content": text_content,
                "metadata": metadata,
                "status": "completed"
            }
            
        except Exception as e:
            return {
                "url": url,
                "title": "",
                "content": "",
                "metadata": {"error": str(e)},
                "status": "error"
            }
    
    def _extract_text(self, soup: BeautifulSoup) -> str:
        """Extract clean text content from HTML"""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text()
        
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def _extract_metadata(self, soup: BeautifulSoup, url: str) -> Dict:
        """Extract metadata from HTML"""
        metadata = {"url": url}
        
        # Extract meta tags
        meta_tags = soup.find_all("meta")
        for tag in meta_tags:
            if tag.get("name") == "description":
                metadata["description"] = tag.get("content", "")
            elif tag.get("property") == "og:title":
                metadata["og_title"] = tag.get("content", "")
            elif tag.get("property") == "og:description":
                metadata["og_description"] = tag.get("content", "")
        
        # Extract domain
        parsed_url = urlparse(url)
        metadata["domain"] = parsed_url.netloc
        
        return metadata