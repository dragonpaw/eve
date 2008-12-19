from django_extensions.management.jobs import BaseJob
import pysvn
from PIL import Image
import os
import re
from eve import settings

icon_dirs = (
    'alliances',
    'blueprint',
    'deployable',
    'drone',
    'entity',
    'icons',
    'ship',
    'station',
    'structure',
)

base_dir = os.path.join(settings.STATIC_DIR, 'ccp-icons')

def die(error):
    raise error

class Job(BaseJob):
    """At one point, this converted everything to jpg, but transparent images
    are nice, so we stopped that."""

    help = "Convert the CCP icons to jpg and check them into subversion."
    when = 'never'
    client = pysvn.Client()

    def convert_file(self, file):
        print "Converting: %s" % file
        name, ext = os.path.splitext(file)
        im = Image.open(file)
        new = name + '.jpg'
        print "Output: %s" % new
        im.save(new, 'jpeg')
        self.client.add(new)
        self.client.remove(file)

    def rename_dir(self, dir):
        pattern = re.compile(r'^(\d+)_(\1)$')
        match = pattern.search(dir)
        if not match:
            return False

        new = pattern.replace(match.group(1), dir)
        print "Rename dir: %s to %s" % (dir, new)
        #os.rename(dir, new)

    def process_dir(self, dir):
        print "Processing: %s" % dir
        for root, dirs, files in os.walk(dir, onerror=die, topdown=False):
            for f in files:
                if f.endswith('.png'):
                    f = os.path.join(root, f)
                    self.convert_file(f)

    def execute(self):
        return None

        for dir in icon_dirs:
            dir = os.path.join(base_dir, dir)
            self.process_dir(dir)
