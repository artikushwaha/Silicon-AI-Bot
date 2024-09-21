import requests
from bs4 import BeautifulSoup

def crawl_website(base_url, max_pages=100):
    crawled_pages = {}
    to_crawl = [base_url]
    crawled = set()

    while to_crawl and len(crawled_pages) < max_pages:
        url = to_crawl.pop(0)
        if url not in crawled:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            crawled_pages[url] = soup.get_text()  # Store page text

            # Add new links to crawl
            for link in soup.find_all('a', href=True):
                full_link = requests.compat.urljoin(base_url, link['href'])
                if full_link.startswith(base_url):
                    to_crawl.append(full_link)

            crawled.add(url)

    return crawled_pages
