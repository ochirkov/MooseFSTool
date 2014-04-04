import tarfile
import datetime
import os

def create_targz(path, source_dir):
    output_filename = os.path.join(path,
        datetime.datetime.now().strftime("%d_%b_%Y") + '_mfs_backup.tar.gz')
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir)