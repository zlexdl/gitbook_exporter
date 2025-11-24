import requests
from bs4 import BeautifulSoup

url = "https://docs.nado.xyz/"
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

print("Classes of divs:")
classes = set()
for div in soup.find_all('div', class_=True):
    for c in div['class']:
        classes.add(c)
print(classes)

print("\nNav elements:")
for nav in soup.find_all('nav'):
    print(nav.prettify()[:500])

print("\nLinks in potential sidebar:")
# GitBook often uses these classes
for cls in ['summary', 'book-summary', 'gitbook-summary', 'sidebar', 'nav']:
    found = soup.find(class_=cls)
    if found:
        print(f"Found class '{cls}':")
        # print(found.prettify()[:200])
        links = found.find_all('a')
        print(f"  Found {len(links)} links")
        for a in links[:3]:
            print(f"  - {a.get('href')}")
