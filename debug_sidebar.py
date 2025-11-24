import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

url = "https://docs.nado.xyz/developer-resources/api"
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
}

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    
    print(f"Page title: {soup.title.string if soup.title else 'No title'}")
    
    # Try to find sidebar links
    # Strategy 1: Look for 'nav'
    navs = soup.find_all('nav')
    print(f"Found {len(navs)} nav elements")
    
    # Strategy 2: Look for links that look like sidebar links (relative paths, distinct from main content)
    # Modern GitBook often puts sidebar in a div with specific classes or just a long list of links
    
    # Let's print all links to see if we can spot a pattern
    links = soup.find_all('a', href=True)
    print(f"Total links found: {len(links)}")
    
    # Filter for internal links
    internal_links = []
    for a in links:
        href = a['href']
        if href.startswith('/') or href.startswith(url):
            internal_links.append(href)
            
    print(f"Internal links (first 20): {internal_links[:20]}")
    
    # Check for specific GitBook classes
    sidebar = soup.find('div', {'data-testid': 'sidebar'}) # Hypothetical
    if not sidebar:
        # Try to find a div that contains many of these internal links
        pass

except Exception as e:
    print(f"Error: {e}")
