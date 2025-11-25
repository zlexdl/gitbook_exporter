# GitBook Exporter

A Python tool to export GitBook documentation to Markdown and HTML formats.

## Features

- **Recursive Crawling**: Automatically discovers pages using `GitbookLoader` or falls back to recursive crawling via sidebar links.
- **Dual Output**: Exports content as both HTML and Markdown.
- **Scope Restriction**: Restricts crawling to the specified base URL path.
- **Single File Mode**: Option to combine all Markdown content into a single file (`full_book.md`).
- **Format Selection**: Choose to export only HTML, only Markdown, or both.

## Installation

1. Clone the repository.
2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Basic usage:
```bash
python main.py <gitbook_url>
```

### Options

- `--output`, `-o`: Specify output directory (default: `output`).
- `--single-file`, `-s`: Generate a single Markdown file containing all pages (only applies to Markdown output).
- `--format`, `-f`: Specify output format. Choices: `html`, `md`, `all` (default: `all`).

### Examples

Export entire site to default output directory:
```bash
python main.py https://docs.example.com
```

Export a specific section to a single Markdown file:
```bash
python main.py https://docs.example.com/section/api --single-file --format md
```

## Output Structure

The tool creates a directory structure in the output folder based on the domain name:

```
output/
  docs.example.com/
    html/       # HTML files
    md/         # Markdown files
    full_book.md # (Optional) Combined Markdown file
```
