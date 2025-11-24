import os
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from urllib.parse import urlparse, urljoin
import time
from langchain_community.document_loaders import GitbookLoader

class GitBookExporter:
    def __init__(self, base_url, output_dir="output", single_file=False, format="all"):
        self.base_url = base_url.rstrip('/')
        self.domain = urlparse(base_url).netloc
        self.base_path = urlparse(base_url).path
        self.output_dir = os.path.join(output_dir, self.domain)
        self.single_file = single_file
        self.format = format
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
        })
        self.visited = set()
        self.markdown_buffer = []

    def get_soup(self, url):
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    def clean_url(self, url):
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

    def is_internal(self, url):
        parsed = urlparse(url)
        if parsed.netloc != self.domain:
            return False
        # Check if path starts with base_path
        # Handle case where base_path is empty (root)
        if not self.base_path:
            return True
        return parsed.path.startswith(self.base_path)

    def extract_content(self, soup):
        content = soup.find('main') or soup.find('article') or soup.find('div', class_='page-inner') or soup.find('div', id='book-search-results')
        
        if not content:
            return None, None

        html_content = str(content)
        
        for tag in content.find_all(['script', 'style', 'nav']):
            tag.decompose()
            
        markdown_content = md(str(content))
        return html_content, markdown_content

    def extract_links(self, soup, current_url):
        links = [] # Use list to preserve order
        # Search in both nav and aside (common for sidebars)
        containers = soup.find_all(['nav', 'aside'])
        
        for container in containers:
            for a in container.find_all('a', href=True):
                href = a['href']
                full_url = urljoin(current_url, href)
                if self.is_internal(full_url):
                    cleaned = self.clean_url(full_url)
                    if cleaned not in links:
                        links.append(cleaned)
        return links

    def save_content(self, url, html_content, markdown_content):
        parsed_url = urlparse(url)
        path = parsed_url.path
        
        if path.startswith('/'):
            path = path[1:]
            
        if not path:
            path = "index"
        
        if path.endswith('.html'):
            path = path[:-5]
            
        html_dir = os.path.join(self.output_dir, 'html', os.path.dirname(path))
        md_dir = os.path.join(self.output_dir, 'md', os.path.dirname(path))
        
        if self.format in ['html', 'all']:
            os.makedirs(html_dir, exist_ok=True)
            filename = os.path.basename(path)
            if not filename:
                filename = "index"
            with open(os.path.join(html_dir, f"{filename}.html"), 'w', encoding='utf-8') as f:
                f.write(html_content)
            
        if self.format in ['md', 'all']:
            os.makedirs(md_dir, exist_ok=True)
            filename = os.path.basename(path)
            if not filename:
                filename = "index"
            
            if self.single_file:
                # Add header to distinguish pages
                header = f"\n\n# {url}\n\n"
                self.markdown_buffer.append(header + markdown_content)
            else:
                with open(os.path.join(md_dir, f"{filename}.md"), 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
            
        print(f"Processed {url}")

    def save_single_markdown(self):
        if not self.markdown_buffer:
            return
            
        output_file = os.path.join(self.output_dir, "full_book.md")
        os.makedirs(self.output_dir, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(self.markdown_buffer))
        print(f"Saved single markdown file to {output_file}")

    def run_fallback(self):
        print("Falling back to recursive crawling...")
        # Use a stack for DFS to try to approximate book order (if links are in order)
        # But wait, standard DFS reverses the order of children if pushed to stack.
        # To preserve order: reverse links before pushing.
        
        stack = [self.base_url]
        self.visited.add(self.clean_url(self.base_url))
        
        while stack:
            current_url = stack.pop()
            print(f"Processing {current_url}...")
            
            soup = self.get_soup(current_url)
            if not soup:
                continue
                
            html_content, markdown_content = self.extract_content(soup)
            if html_content:
                self.save_content(current_url, html_content, markdown_content)
            
            # Find new links
            links = self.extract_links(soup, current_url)
            # Reverse links so that the first link is popped first (DFS)
            for link in reversed(links):
                cleaned_link = self.clean_url(link)
                if cleaned_link not in self.visited:
                    self.visited.add(cleaned_link)
                    stack.append(cleaned_link)
            
            time.sleep(0.2)
            
        if self.single_file:
            self.save_single_markdown()

    def run(self):
        print(f"Discovering pages from {self.base_url} using GitbookLoader...")
        documents = []
        try:
            loader = GitbookLoader(self.base_url, load_all_paths=True)
            documents = loader.load()
        except Exception as e:
            print(f"GitbookLoader failed: {e}")
        
        if not documents:
            print("No documents found with GitbookLoader (possibly missing sitemap).")
            self.run_fallback()
            return

        print(f"Found {len(documents)} pages. Starting export...")
        
        # Deduplicate URLs and filter by scope
        urls = sorted(list(set(doc.metadata.get('source') for doc in documents if doc.metadata.get('source'))))
        urls = [url for url in urls if self.is_internal(url)]
        
        print(f"Filtered to {len(urls)} pages within scope.")
        
        for i, url in enumerate(urls):
            print(f"[{i+1}/{len(urls)}] Processing {url}...")
            
            soup = self.get_soup(url)
            if not soup:
                continue
                
            html_content, markdown_content = self.extract_content(soup)
            if html_content:
                self.save_content(url, html_content, markdown_content)
            
            time.sleep(0.2)
            
        if self.single_file:
            self.save_single_markdown()
