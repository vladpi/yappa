import logging
import os
import subprocess
import sys
from contextlib import suppress
from pathlib import Path
from shutil import copy2, copytree, ignore_patterns, make_archive

import boto3
from botocore.session import Session as BotocoreSession

from yappa.settings import DEFAULT_IGNORED_FILES, DEFAULT_PACKAGE_DIR, \
    DEFAULT_REQUIREMENTS_FILE, \
    HANDLER_FILENAME, YANDEX_S3_URL

logger = logging.getLogger(__name__)


def prepare_package(requirements_file=DEFAULT_REQUIREMENTS_FILE,
                    ignored_files=DEFAULT_IGNORED_FILES,
                    tmp_dir=DEFAULT_PACKAGE_DIR, to_install_requirements=True):
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
    if to_install_requirements:
        logger.info('Installing requirements...')
        cmd = (
            f'{sys.executable} -m pip install '
            f'-r {requirements_file} -t {tmp_dir} --upgrade --quiet'
        )
        subprocess.check_call(cmd.split())
    return tmp_dir


def get_s3_resource(profile_name):
    session = BotocoreSession()
    config = session.full_config
    profile = config['profiles'][profile_name]
    s3 = boto3.resource(
        's3',
        aws_access_key_id=profile['aws_access_key_id'],
        aws_secret_access_key=profile['aws_secret_access_key'],
        endpoint_url=YANDEX_S3_URL,
    )
    return s3


def ensure_bucket(bucket_name, profile_name):
    s3 = get_s3_resource(profile_name)
    bucket = s3.Bucket(bucket_name)
    try:
        bucket.create()
    except Exception as e:
        if e.__class__.__name__ != 'BucketAlreadyOwnedByYou':
            raise
    return bucket


def upload_to_bucket(folder, bucket_name, profile_name, ):
    """
    makes archive, uploads to bucket, deletes tmp archive
    """
    logger.info("Creating zip package")
    archive_path = make_archive(folder, 'zip', folder)
    archive_filename = os.path.basename(archive_path)
    try:
        bucket = ensure_bucket(bucket_name, profile_name)
        bucket.upload_file(archive_filename, archive_filename)
    finally:
        os.remove(archive_filename)
    return archive_filename


def delete_bucket(bucket_name, profile_name):
    """
    deletes bucket from s3
    """
    bucket = ensure_bucket(bucket_name, profile_name)
    bucket.objects.all().delete()
    bucket.delete()
