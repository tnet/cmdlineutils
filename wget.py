import io
import urllib.request

import click

from common import *

colorama.init(autoreset=True)


@click.command()
@click.argument('url', metavar="URL_ADDRESS")
@click.option('-o', '--output', metavar="FILE", help='Output file. If not specified, default filename will be used')
def main_function(url, output):
    """Loads URL address"""
    if not url.startswith('http://'):
        url = f"http://{url}"
    page = urllib.request.urlopen(url).read()
    if not output:
        filename = os.path.basename(url)
    else:
        filename = output
    f = io.open(filename, 'wb')
    f.write(page)
    click.echo(Fore.GREEN + "Output written to %s" % filename)
    f.close()


if __name__ == "__main__":
    script_handler(main_function)
