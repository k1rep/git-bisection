"""
This script downloads the Z3 binary release for a given version and extracts it to a specified directory.
"""
import os
import requests
import zipfile
import logging

logging.basicConfig(level=logging.INFO)

version_to_suffix = {
        '4.8.10': 'x64-ubuntu-18.04.zip',
        '4.6.0': 'x64-ubuntu-16.04.zip',
        '4.13.0': 'x64-glibc-2.35.zip', '4.12.6': 'x64-glibc-2.35.zip',
        '4.12.5': 'x64-glibc-2.35.zip', '4.12.4': 'x64-glibc-2.35.zip',
        '4.12.3': 'x64-glibc-2.35.zip', '4.12.2': 'x64-glibc-2.35.zip',
        '4.12.1': 'x64-glibc-2.35.zip', '4.12.0': 'x64-glibc-2.35.zip',
        '4.11.2': 'x64-glibc-2.31.zip', '4.11.0': 'x64-glibc-2.31.zip',
        '4.10.2': 'x64-glibc-2.31.zip', '4.10.1': 'x64-glibc-2.31.zip',
        '4.10.0': 'x64-glibc-2.31.zip', '4.9.1': 'x64-glibc-2.31.zip',
        '4.9.0': 'x64-glibc-2.31.zip', '4.8.17': 'x64-glibc-2.31.zip',
        '4.8.16': 'x64-glibc-2.31.zip', '4.8.15': 'x64-glibc-2.31.zip',
        '4.8.14': 'x64-glibc-2.31.zip', '4.8.13': 'x64-glibc-2.31.zip',
        '4.8.12': 'x64-glibc-2.31.zip', '4.8.11': 'x64-glibc-2.31.zip',
        '4.4.0': 'x64-ubuntu-14.04.zip', '4.4.1': 'x64-ubuntu-14.04.zip',
        '4.5.0': 'x64-ubuntu-14.04.zip',
        '4.8.6': 'x64-ubuntu-16.04.zip', '4.8.7': 'x64-ubuntu-16.04.zip',
        '4.8.8': 'x64-ubuntu-16.04.zip', '4.8.9': 'x64-ubuntu-16.04.zip'
    }


def download_file(url, save_as):
    response = requests.get(url)
    if response.status_code == 200:
        with open(save_as, 'wb') as f:
            f.write(response.content)
        logging.info(f"File downloaded and saved to {save_as}")
        return save_as
    else:
        logging.error(f"Failed to download the file.")
        return None


def unzip_file(zip_path, extract_to):
    """解压文件到指定目录"""
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
            logging.info(f"Extraction complete to {extract_to}")
    except FileNotFoundError:
        logging.error(f"ZIP file not found.")


def get_z3_release(version, download_dir, unzip_dir):
    base_url = "https://github.com/Z3Prover/z3/releases/download"
    # Default suffix if version not found in dictionary
    default_suffix = 'x64-ubuntu-16.04.zip'
    filename = f"z3-{version}-{version_to_suffix.get(version, default_suffix)}"
    url = f"{base_url}/z3-{version}/{filename}"
    zip_path = os.path.join(download_dir, filename)
    # 如果zip文件已存在，跳过
    if os.path.exists(zip_path):
        logging.info(f"File already exists: {zip_path}")
        return
    # Download and save the file
    downloaded_file = download_file(url, zip_path)
    if downloaded_file:
        # Unzip the file
        unzip_file(downloaded_file, unzip_dir)


if __name__ == '__main__':
    version_tag = version_to_suffix.keys()
    for vt in version_tag:
        get_z3_release(vt, '/home/uu613/workspace/', '/home/uu613/workspace/z3_versions')
