from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import aiohttp
from typing import Dict, Optional
import asyncio
from urllib.parse import urlparse
import re
import PyPDF2
import io

class WebScraper:
    def __init__(self):
        self.session = None

    async def scrape_url(self, url: str) -> Dict:
        """Main scraping method that handles different content types"""
        try:
            # Check if URL is a PDF
            if url.lower().endswith('.pdf') or '/pdf/' in url.lower():
                return await self._scrape_pdf(url)

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

    async def _scrape_pdf(self, url: str) -> Dict:
        """Download and extract text from PDF URL"""
        try:
            # Download PDF
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        raise Exception(f"Failed to download PDF: HTTP {response.status}")

                    pdf_content = await response.read()

            # Extract text from PDF
            pdf_file = io.BytesIO(pdf_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)

            # Extract text with page markers
            text_content = ""
            page_markers = []  # Track where each page starts

            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()

                # Record the character position where this page starts
                page_markers.append({
                    "page": page_num + 1,
                    "start_pos": len(text_content)
                })

                # Add page marker in the text itself
                text_content += f"[PAGE {page_num + 1}]\n{page_text}\n\n"

            # Extract title from PDF metadata or URL
            title = ""
            if pdf_reader.metadata and pdf_reader.metadata.get('/Title'):
                title = pdf_reader.metadata.get('/Title')
            else:
                # Try to extract from URL
                title = url.split('/')[-1].replace('.pdf', '').replace('_', ' ').replace('-', ' ')

            return {
                "url": url,
                "title": title or "PDF Document",
                "content": text_content.strip(),
                "metadata": {
                    "url": url,
                    "domain": urlparse(url).netloc,
                    "type": "pdf",
                    "pages": len(pdf_reader.pages),
                    "page_markers": page_markers
                },
                "status": "completed"
            }

        except Exception as e:
            return {
                "url": url,
                "title": "",
                "content": "",
                "metadata": {"error": str(e), "type": "pdf"},
                "status": "error"
            }