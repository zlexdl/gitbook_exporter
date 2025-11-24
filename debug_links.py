import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

url = "https://docs.nado.xyz/developer-resources/api"
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
}

def clean_url(url):
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

def is_internal(url, domain):
    return urlparse(url).netloc == domain

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')
domain = urlparse(url).netloc

print(f"Domain: {domain}")

nav = soup.find('nav')
if nav:
    print("Found nav element.")
    links = []
    for a in nav.find_all('a', href=True):
        href = a['href']
        full_url = urljoin(url, href)
        if is_internal(full_url, domain):
            cleaned = clean_url(full_url)
            links.append(cleaned)
    
    print(f"Found {len(links)} internal links in nav.")
    for link in links[:10]:
        print(f" - {link}")
else:
    print("No nav element found.")
    # Try finding sidebar div
    sidebar = soup.find('div', class_=lambda x: x and 'sidebar' in x)
    if sidebar:
        print(f"Found sidebar div: {sidebar.get('class')}")
    else:
        print("No sidebar div found.")

# Check for specific links we expect
expected = "https://docs.nado.xyz/developer-resources/api/endpoints"
print(f"\nChecking for expected link: {expected}")
found = False
for a in soup.find_all('a', href=True):
    href = a['href']
    full = urljoin(url, href)
    if clean_url(full) == expected:
        print(f"Found expected link in tag: {a}")
        found = True
        # Check if it's inside nav
        parents = [p.name for p in a.parents]
        print(f"Parents: {parents}")
        break

if not found:
    print("Expected link NOT found in the entire soup.")
