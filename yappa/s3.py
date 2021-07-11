import logging
import os
import subprocess
import sys
from contextlib import suppress
from pathlib import Path
from shutil import copytree, ignore_patterns, make_archive

import boto3

from yappa.handlers.wsgi import DEFAULT_CONFIG_FILENAME
from yappa.settings import DEFAULT_IGNORED_FILES, DEFAULT_PACKAGE_DIR, \
    DEFAULT_REQUIREMENTS_FILE, \
    HANDLERS_DIR, YANDEX_S3_URL

logger = logging.getLogger(__name__)


def prepare_package(requirements_file=DEFAULT_REQUIREMENTS_FILE,
                    ignored_files=DEFAULT_IGNORED_FILES,
                    tmp_dir=DEFAULT_PACKAGE_DIR, to_install_requirements=True,
                    config_filename=DEFAULT_CONFIG_FILENAME):
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
    copytree(Path(Path(__file__).resolve().parent, HANDLERS_DIR),
             Path(tmp_dir, "handlers"), dirs_exist_ok=True)
    os.rename(Path(tmp_dir, config_filename),
              Path(tmp_dir, DEFAULT_CONFIG_FILENAME))
    if to_install_requirements:
        logger.info('Installing requirements...')
        cmd = (
            f'{sys.executable} -m pip install '
            f'-r {requirements_file} -t {tmp_dir} --upgrade --quiet'
        )
        subprocess.check_call(cmd.split())
    return tmp_dir


def ensure_bucket(bucket_name, aws_access_key_id, aws_secret_access_key):
    s3 = boto3.resource(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        endpoint_url=YANDEX_S3_URL,
    )
    bucket = s3.Bucket(bucket_name)
    try:
        bucket.create()
    except Exception as e:
        if e.__class__.__name__ != 'BucketAlreadyOwnedByYou':
            raise
    return bucket


def upload_to_bucket(folder, bucket_name, aws_access_key_id,
                     aws_secret_access_key):
    """
    makes archive, uploads to bucket, deletes tmp archive
    """
    logger.info("Creating zip package")
    archive_path = make_archive(folder, 'zip', folder)
    archive_filename = os.path.basename(archive_path)
    try:
        bucket = ensure_bucket(bucket_name, aws_access_key_id=aws_access_key_id,
                               aws_secret_access_key=aws_secret_access_key, )
        bucket.upload_file(archive_filename, archive_filename)
    finally:
        os.remove(archive_filename)
    return archive_filename


def delete_bucket(bucket_name, aws_access_key_id, aws_secret_access_key):
    """
    deletes bucket from s3
    """
    bucket = ensure_bucket(bucket_name, aws_access_key_id=aws_access_key_id,
                           aws_secret_access_key=aws_secret_access_key, )
    bucket.objects.all().delete()
    bucket.delete()
