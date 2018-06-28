import datetime

import click

from common import *


def GetDate1(dirfile):
    filename = os.path.split(dirfile)[1]
    try:
        date = datetime.datetime.strptime(filename[0:8], '%Y%m%d').date()
    except ValueError:
        return None
    return date


def GetDate2(dirfile):
    filename = os.path.split(dirfile)[1]
    if not (filename.startswith("IMG-") or filename.startswith('VID-')):
        return None
    return GetDate1(filename[4:])


def GetDate3(dirfile):
    filename = os.path.split(dirfile)[1]
    if not filename.endswith(".jpeg") and not filename.endswith(".jpg"):
        return None
    last_modified_date = datetime.datetime.fromtimestamp(os.path.getmtime(dirfile))
    return last_modified_date


def GetDate(dirfile):
    for f in [GetDate1, GetDate2, GetDate3]:
        d = f(dirfile)
        if d is not None:
            return d
    return None


def DirectoryFromDate(date):
    return datetime.datetime.strftime(date, "%Y_%m_%d")


def ProcessDirectory(dir):
    i = 0
    for file in os.listdir(dir):
        dirfile = os.path.join(dir, file)

        if not os.path.isfile(dirfile):
            continue

        date = GetDate(dirfile)
        if not date:
            continue

        subdirname = DirectoryFromDate(date)
        subdir = os.path.join(dir, subdirname)
        if not os.path.exists(subdir):
            os.mkdir(subdir)

        dirfile2 = os.path.join(subdir, file)
        i += 1
        print("Moving '%s' to subdirectory '%s'" % (file, subdirname))
        os.rename(dirfile, dirfile2)
    print("%i files moved" % i)


@click.command()
@click.argument('rootdirectory', metavar="ROOT_DIRECTORY")
def main_function(rootdirectory):
    """This script splits all files in a given directory into subdirectories, according to the file date"""
    verify_path(rootdirectory)
    ProcessDirectory(rootdirectory)


if __name__ == "__main__":
    script_handler(main_function)
