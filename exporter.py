import os
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from urllib.parse import urlparse
import time
from langchain_community.document_loaders import GitbookLoader

class GitBookExporter:
    def __init__(self, base_url, output_dir="output"):
        self.base_url = base_url.rstrip('/')
        self.domain = urlparse(base_url).netloc
        self.output_dir = os.path.join(output_dir, self.domain)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
        })

    def get_soup(self, url):
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    def extract_content(self, soup):
        # Try to find the main content area
        content = soup.find('main') or soup.find('article') or soup.find('div', class_='page-inner') or soup.find('div', id='book-search-results')
        
        if not content:
            # Fallback: try to find the biggest div?
            # Or just return the body
            content = soup.body
        
        if not content:
            return None, None

        # Convert to HTML string
        html_content = str(content)
        
        # Convert to Markdown
        # Remove some elements before converting
        for tag in content.find_all(['script', 'style', 'nav']):
            tag.decompose()
            
        markdown_content = md(str(content))
        return html_content, markdown_content

    def save_content(self, url, html_content, markdown_content):
        # Determine file path based on URL
        # Handle cases where url might not start with base_url (if redirected or something)
        # But GitbookLoader usually returns correct URLs
        
        parsed_url = urlparse(url)
        path = parsed_url.path
        
        if path.startswith('/'):
            path = path[1:]
            
        if not path:
            path = "index"
        
        # Remove extension if present
        if path.endswith('.html'):
            path = path[:-5]
            
        # Create directories
        html_dir = os.path.join(self.output_dir, 'html', os.path.dirname(path))
        md_dir = os.path.join(self.output_dir, 'md', os.path.dirname(path))
        
        os.makedirs(html_dir, exist_ok=True)
        os.makedirs(md_dir, exist_ok=True)
        
        filename = os.path.basename(path)
        if not filename:
            filename = "index"

        # Save HTML
        with open(os.path.join(html_dir, f"{filename}.html"), 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        # Save Markdown
        with open(os.path.join(md_dir, f"{filename}.md"), 'w', encoding='utf-8') as f:
            f.write(markdown_content)
            
        print(f"Saved {url} to {path}")

    def run(self):
        print(f"Discovering pages from {self.base_url} using GitbookLoader...")
        try:
            loader = GitbookLoader(self.base_url, load_all_paths=True)
            documents = loader.load()
        except Exception as e:
            print(f"Error loading GitBook: {e}")
            return

        print(f"Found {len(documents)} pages. Starting export...")
        
        # Deduplicate URLs
        urls = sorted(list(set(doc.metadata.get('source') for doc in documents if doc.metadata.get('source'))))
        
        for i, url in enumerate(urls):
            print(f"[{i+1}/{len(urls)}] Processing {url}...")
            
            soup = self.get_soup(url)
            if not soup:
                continue
                
            html_content, markdown_content = self.extract_content(soup)
            if html_content:
                self.save_content(url, html_content, markdown_content)
            
            time.sleep(0.2) # Be polite

