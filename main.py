import click
from exporter import GitBookExporter

@click.command()
@click.argument('url')
@click.option('--output', '-o', default='output', help='Output directory')
@click.option('--single-file', '-s', is_flag=True, help='Generate a single Markdown file')
@click.option('--format', '-f', type=click.Choice(['html', 'md', 'all'], case_sensitive=False), default='all', help='Output format (html, md, or all)')
def main(url, output, single_file, format):
    """Export a GitBook to Markdown and HTML."""
    click.echo(f"Exporting GitBook from {url} to {output}...")
    exporter = GitBookExporter(url, output, single_file, format)
    exporter.run()
    click.echo("Done!")

if __name__ == '__main__':
    main()
