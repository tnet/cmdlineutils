import PIL
import click
import datetime
import imagehash
import io
import json
import re

from common import *

colorama.init(autoreset=True)
cache_saving_frequency = 10
save_errors = True


class ImageHashEngine:
    def __init__(self, cache_location):
        self.lastsave = datetime.datetime.now()
        self.cache_location = cache_location
        if os.path.exists(self.cache_location):
            with open(self.cache_location) as reader:
                jsondata = reader.read()
            self.jsondata = json.loads(jsondata)
            # print("ImageHashEngine: Loaded cache with %i entries" % len(self.jsondata))
        else:
            self.jsondata = dict()

    def save(self, force=False):
        if (datetime.datetime.now() - self.lastsave).seconds > cache_saving_frequency or force:
            # print("Saving cache ...")
            self.lastsave = datetime.datetime.now()
            jsonstr = json.dumps(self.jsondata, sort_keys=True, indent=4)
            with open(self.cache_location, 'w') as writer:
                writer.write(jsonstr)

    def get_hash(self, filename):
        filename = os.path.abspath(filename)
        to_return = None
        if filename in self.jsondata:
            to_return = self.jsondata[filename]
            if to_return.startswith("Error"):
                return None
            to_return = imagehash.hex_to_hash(to_return)
            return to_return

        hash = None
        strhash = None
        try:
            image = PIL.Image.open(filename)
            hash = imagehash.average_hash(image)
            strhash = str(hash)
            self.jsondata[filename] = strhash
        except BaseException as ex:
            hash = None
            strhash = "Error: %s" % str(ex)
            print(colorama.Back.RED + "Exception %s when processing %s" % (str(ex), filename))
            if save_errors:
                self.jsondata[filename] = strhash
        self.save()
        return hash


class ImageHash:
    def __init__(self, file, hash):
        self.file = file
        self.hash = hash


class Cluster:
    def __init__(self, first_item):
        self.items = list()
        self.items.append(first_item)
        self.max_distance = 0

    def add(self, ih):
        for item in self.items:
            self.max_distance = max(self.max_distance, item.hash - ih.hash)
        self.items.append(ih)

    def distance(self, ih):
        mind = 999999999
        for item in self.items:
            d = item.hash - ih.hash
            mind = min(d, mind)
        return mind


def IsImage(filename):
    f = filename.lower()
    if f.endswith(".jpg"): return True
    if f.endswith(".jpeg"): return True
    return False


def walkdirectory(rootdirectory, regex_search_pattern):
    root_subdirs_files = list()
    for root, subdirs, files in os.walk(rootdirectory):
        if not re.search(regex_search_pattern, root):
            continue
        root_subdirs_files.append((root, subdirs, files))
    i = 0
    n = len(root_subdirs_files)
    for root, subdirs, files in sorted(root_subdirs_files):
        yield i, n, root, subdirs, files
        i += 1


htmlTemplate = '''<html>
    <style>
        #listing {
            display: inline-block; 
            width: 700px;
            height: 100px;
            background-color:white;
            height:99%;
            overflow: scroll;
        }
        #preview {
            background-color:grey;
            display: inline-block; 
            height:99%;
            width: 1000px;
            background-size: 100%;
            background-repeat: no-repeat;
        }
        #exportButton {
            display: inline-block; 
        }
        body {
            background-color:black;
        }
    </style>
<body>
    <button onclick="exportData()" id="exportButton">export</button>
    <div id="listing">
        TEMPLATE_PLACEHOLDER    
    </div>
    <div id="preview"/>
    <script>
        function saveTextAsFile(textToSave)
        {
            var textToSaveAsBlob = new Blob([textToSave], {type:"text/plain"});
            var textToSaveAsURL = window.URL.createObjectURL(textToSaveAsBlob);
            var fileNameToSaveAs = "checkedFiles.txt";
         
            var downloadLink = document.createElement("a");
            downloadLink.download = fileNameToSaveAs;
            downloadLink.innerHTML = "Download File";
            downloadLink.href = textToSaveAsURL;
            downloadLink.onclick =     destroyClickedElement;
            downloadLink.style.display = "none";
            document.body.appendChild(downloadLink);
         
            downloadLink.click();
        }    
        
        function destroyClickedElement(event)
        {
            document.body.removeChild(event.target);
        }
    
        function exportData()
        {
            str = "";
            var elem = document.getElementsByClassName('fileCheckbox');
            for(var i = 0; i < elem.length; i++)
            {
                if (elem[i].checked)
                    str += elem[i].value + "\\r\\n";
            }
            saveTextAsFile(str);
        }
        function displayImg(txt)
        {
            document.getElementById("preview").style.backgroundImage = "url('"+txt+"')";
        }
    </script>
</body>
</html>'''


def get_similar_images(rootdirectory, imagehashes, distance_threshold=3):
    clusters = list()
    n = len(imagehashes)
    i = 0
    for file, hash in sorted(imagehashes.items()):
        i += 1
        print("Processing image hash %i/%i            \r" % (i, n), end="")
        if hash is None:
            continue
        ih = ImageHash(file, hash)
        nearestCluster = None
        nearestDistance = 999999999
        for cluster in clusters:
            d = cluster.distance(ih)
            if d < nearestDistance:
                nearestCluster = cluster
                nearestDistance = d
        if nearestDistance < distance_threshold:
            nearestCluster.add(ih)
        else:
            c = Cluster(ih)
            clusters.append(c)

    htmllinks = io.StringIO()

    counter = 0
    for c in sorted(clusters, reverse=False, key=lambda c: c.max_distance):
        if len(c.items) <= 1:
            continue
        print("<b>Count: %i, Dispersion: %i</b><br>" % (len(c.items), c.max_distance), file=htmllinks)
        for ih in sorted(c.items, key=lambda item: os.path.getsize(item.file), reverse=True):
            title = "%s" % (ih.file)
            filenameForHtml = ih.file.replace('\\', '/')
            print("""<input type="checkbox" class="fileCheckbox" value="%s"></input>
            <a href='#' onclick='displayImg("%s")'>%s</a><br>""" % (filenameForHtml, filenameForHtml, title), file=htmllinks)
            counter += 1

    html = htmlTemplate.replace('TEMPLATE_PLACEHOLDER', htmllinks.getvalue())
    with open(os.path.join(rootdirectory, ".image-report.html"), 'w') as writer:
        print(html, file=writer)
    if counter > 0:
        print(80 * " ", end="\r")
        print("%i differences found" % counter)


@click.command()
@click.argument('rootdirectory', metavar="ROOT_DIRECTORY")
@click.option('regex_search_pattern', '-r', '--regex', default='x', metavar="REGEX", help='Search pattern for subdirectories. Default is .*')
def main_function(rootdirectory, regex_search_pattern):
    """Finds duplicate images based on "soft" similarity comparison"""
    print(colorama.Fore.CYAN + "Walking directory '%s'" % rootdirectory)
    imagehashes = dict()
    imageHashEngine = ImageHashEngine(os.path.join(rootdirectory, ".image_hashes"))

    for i, n, root, subdirs, files in walkdirectory(rootdirectory, regex_search_pattern):
        print("\r" + 80 * " ", end="\r")
        print(colorama.Fore.LIGHTMAGENTA_EX + "%5i/%5i" % (i + 1, n), end=" ")
        print("Directory %s " % root, end="")

        for j, f in enumerate(files):
            ff = os.path.join(root, f)
            if IsImage(f):
                hash = imageHashEngine.get_hash(ff)
                imagehashes[ff] = hash
    imageHashEngine.save(True)
    print()

    get_similar_images(rootdirectory, imagehashes)


if __name__ == "__main__":
    script_handler(main_function)
