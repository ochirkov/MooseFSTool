import tarfile
import datetime
import os

def create_targz(path, metafile):
    arcname = os.path.join(path,
        datetime.datetime.now().strftime("%d%m%Y-%H%M%S") + '_mfs_metadata.tar.gz')
    with tarfile.open(arcname, "w:gz") as tar:
        tar.add(metafile)