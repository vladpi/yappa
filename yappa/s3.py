import logging
import os
import subprocess
import sys
from contextlib import suppress
from pathlib import Path
from shutil import copy2, copytree, ignore_patterns, make_archive, rmtree

from yappa.settings import DEFAULT_PACKAGE_DIR, HANDLER_FILENAME

logger = logging.getLogger(__name__)


def prepare_package(requirements_file, ignored_files,
                    tmp_dir=DEFAULT_PACKAGE_DIR):
    """
    prepares package folder
    - copy project files
    - copy handler.py
    - install packages
    """
    logger.info('Copying project files to %s', tmp_dir)
    with suppress(FileExistsError):
        os.mkdir(tmp_dir)
    copytree(os.getcwd(), tmp_dir,
             ignore=ignore_patterns(*ignored_files, tmp_dir),
             dirs_exist_ok=True)
    copy2(Path(Path(__file__).resolve().parent, HANDLER_FILENAME),
          tmp_dir)
    logger.info('Installing requirements...')
    cmd = (
        f'{sys.executable} -m pip install '
        f'-r {requirements_file} -t {tmp_dir} --upgrade --quiet'
    )
    subprocess.check_call(cmd.split())


def cleanup(folder=DEFAULT_PACKAGE_DIR):
    """
    deletes tmp package folder
    """
    rmtree(folder)


def upload_to_bucket(folder, bucket):
    """
    makes archive, uploads to bucket, deletes tmp archive
    """
    logger.info("Creating zip package")
    make_archive(folder, 'zip', folder)


def delete_bucket(bucket_name):
    """
    deletes bucket from s3
    """
