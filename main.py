import click
from exporter import GitBookExporter

@click.command()
@click.argument('url')
@click.option('--output', '-o', default='output', help='Output directory')
def main(url, output):
    """Export a GitBook to Markdown and HTML."""
    click.echo(f"Exporting GitBook from {url} to {output}...")
    exporter = GitBookExporter(url, output)
    exporter.run()
    click.echo("Done!")

if __name__ == '__main__':
    main()
