import logging
import httpx
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException, Query
from typing import Optional, Dict, Any

# --- Configuration & Setup ---

# Configure logging to track application behavior and errors
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# FastAPI application initialization
app = FastAPI(
    title="Lubimyczytac.pl ISBN Scraper",
    description="A simple API to fetch book descriptions from lubimyczytac.pl using ISBN."
)

class LubimyCzytacScraper:
    """
    A service class dedicated to scraping book information from lubimyczytac.pl.
    """
    
    BASE_URL = "https://lubimyczytac.pl"
    SEARCH_URL = f"{BASE_URL}/szukaj/ksiazki"
    
    # Modern User-Agent to mimic a real browser and avoid basic bot detection
    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    def __init__(self):
        # We use a persistent client if we were doing many requests, 
        # but for this simple script, we'll manage it per request or via context manager.
        pass

    async def get_book_url_from_query(self, query: str) -> Optional[str]:
        """
        Searches for a book by its title/query and returns the absolute URL to its page.
        
        Args:
            query: The search query (e.g., book title).
            
        Returns:
            The full URL to the book page if found, otherwise None.
        """
        params = {"phrase": query}
        
        try:
            async with httpx.AsyncClient(headers=self.HEADERS, follow_redirects=True, timeout=10.0) as client:
                response = await client.get(self.SEARCH_URL, params=params)
                response.raise_for_status()
                
                # Check if we were redirected directly to a book page
                if "/ksiazka/" in str(response.url):
                    logger.info(f"Direct redirect to book page for query '{query}': {response.url}")
                    return str(response.url)

                soup = BeautifulSoup(response.text, "html.parser")
                
                # Primary selector: The title link in the search results
                book_link_element = soup.select_one("a.authorAllBooks__singleTextTitle")
                
                # Fallback selectors for different layout versions or unexpected results
                if not book_link_element:
                    logger.debug(f"Primary selector failed for query '{query}', trying fallbacks.")
                    book_link_element = (
                        soup.select_one(".book-list-item__title a") or 
                        soup.select_one("a[href*='/ksiazka/']")
                    )
                
                if book_link_element and 'href' in book_link_element.attrs:
                    url = book_link_element['href']
                    # Ensure the URL is absolute
                    if not url.startswith("http"):
                        url = f"{self.BASE_URL}{url}"
                    return url
                
                return None
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error searching for query '{query}': {e.response.status_code}")
        except Exception as e:
            logger.error(f"Unexpected error searching for query '{query}': {e}")
        
        return None

    async def scrape_book_details(self, url: str) -> Dict[str, Any]:
        """
        Scrapes a specific book page for its title, author, and description.
        
        Args:
            url: The absolute URL of the book page.
            
        Returns:
            A dictionary containing title, author, description, and the source URL.
            
        Raises:
            HTTPException: If the page cannot be reached or parsed correctly.
        """
        try:
            async with httpx.AsyncClient(headers=self.HEADERS, follow_redirects=True, timeout=10.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, "html.parser")
                
                # 1. Extract Title
                title_elem = (
                    soup.select_one("h1.bookHeader__title") or 
                    soup.select_one("h1.book__title")
                )
                title = title_elem.get_text(strip=True) if title_elem else "Unknown Title"
                
                # 2. Extract Author
                author_elem = (
                    soup.select_one(".bookHeader__author a") or 
                    soup.select_one("a.link-name")
                )
                author = author_elem.get_text(strip=True) if author_elem else "Unknown Author"

                # 3. Extract Description
                description = self._parse_description(soup)

                return {
                    "title": title,
                    "author": author,
                    "description": description,
                    "url": url
                }
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error scraping {url}: {e.response.status_code}")
            raise HTTPException(status_code=502, detail="External service error (Lubimyczytac)")
        except Exception as e:
            logger.error(f"Error scraping book page {url}: {e}")
            raise HTTPException(status_code=500, detail="Internal error during scraping")

    def _parse_description(self, soup: BeautifulSoup) -> str:
        """
        Helper to extract and clean the book description.
        """
        # .collapse-content is the primary container for the long description
        description_elem = (
            soup.select_one(".collapse-content") or 
            soup.select_one(".book-description")
        )
        
        if not description_elem:
            return ""

        # Clean up the description: remove 'read more' buttons and other UI artifacts
        for junk in description_elem.select(".js-book-read-more, .expand-text-button, .js-expand-desc, .more-desc"):
            junk.decompose()
        
        # Extract text while preserving paragraphs with newlines
        text = description_elem.get_text(separator="\n", strip=True)
        
        # Final cleanup of common Polish phrases left by the scraper
        text = text.replace("... więcej", "").replace("Rozwiń opis", "").strip()
        
        return text

# Instantiate the scraper service
scraper = LubimyCzytacScraper()

# --- API Endpoints ---

@app.get("/book", response_model=Dict[str, Any])
async def search_book(
    title: str = Query(..., description="The title of the book to search for", min_length=2)
):
    """
    Fetch book details (title, author, description) from lubimyczytac.pl 
    using the provided title query.
    """
    logger.info(f"API Request: Metadata for title '{title}'")
    
    # Step 1: Find the book URL
    book_url = await scraper.get_book_url_from_query(title)
    
    if not book_url:
        logger.warning(f"Book with title '{title}' not found.")
        raise HTTPException(
            status_code=404, 
            detail=f"Book with title '{title}' not found on lubimyczytac.pl"
        )
    
    # Step 2: Scrape the details from the book page
    logger.info(f"Found book URL: {book_url}. Proceeding to scrape details.")
    book_data = await scraper.scrape_book_details(book_url)
    
    # Step 3: Enrich with original query and return
    book_data["query"] = title
    return book_data

# --- Entry Point ---

if __name__ == "__main__":
    import uvicorn
    import os
    
    # Allow port to be set via environment variable for flexibility
    port = int(os.environ.get("PORT", 8000))
    
    logger.info(f"Starting server on port {port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
