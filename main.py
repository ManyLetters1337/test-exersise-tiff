import math
import os
import sys
import zipfile
from urllib.parse import urlencode

import requests
from PIL import Image

IMAGE_SIZE = (175, 175)
IMAGES_COLUMN_COUNT = 4
WIDTH_SPACE_SIZE = 150
HEIGHT_SPACE_SIZE = 250
BETWEEN_IMAGES_SPACE_SIZE = 25
BASE_ZIP_DIR = 'Для тестового/'
BASE_URL = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?'
YANDEX_DISK_LINK = 'https://disk.yandex.ru/d/V47MEP5hZ3U1kg'
FILE_NAME = 'Result.tif'


def get_href(public_link: str = ''):
    """
    Get download url
    """
    final_url = BASE_URL + urlencode(dict(public_key=public_link or YANDEX_DISK_LINK))
    response = requests.get(final_url)
    parse_href = response.json()['href']
    return parse_href


def unzip_files(path_to_zip: 'str'):
    """
    Unzip folders from zip
    :param path_to_zip:
    :return:
    """
    with zipfile.ZipFile(path_to_zip, 'r') as zip_ref:
        zip_ref.extractall()


def download_files(url: 'str'):
    """
    Donwload zip
    :param url:
    :return:
    """
    currient_folder = os.getcwd()
    destination_folder = os.path.join(currient_folder, "download_files")

    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    filename = "ImagesZip"
    download_url = requests.get(url)
    final_link = os.path.join(destination_folder, filename)
    with open(final_link, 'wb') as ff:
        ff.write(download_url.content)

    return final_link


def get_files_path(folder: list) -> list:
    """
    Get list with all files path
    :param folder:
    :return: list of files path
    """
    files_list = []
    for subfolder in folder:
        folder_path, dir_path = '', ''
        if os.path.exists(subfolder):
            folder_path = os.path.abspath(subfolder) + '/'
            dir_path = subfolder
        elif os.path.exists(BASE_ZIP_DIR + subfolder):
            folder_path = os.path.abspath(BASE_ZIP_DIR + subfolder) + '/'
            dir_path = BASE_ZIP_DIR + subfolder

        for fl in os.listdir(dir_path):
            if fl.endswith(".png") and folder_path + fl not in files_list:
                files_list.append(folder_path + fl)

    return files_list


def get_strings_count(files_list: list) -> int:
    """
    Get count of stings
    :param files_list: List of files
    :return: int
    """
    return math.ceil(len(files_list) / IMAGES_COLUMN_COUNT)


def get_size(files_list: list) -> tuple[int, int]:
    """
    Get image size
    :param files_list: List of files
    :return: tuple of image sizes
    """
    column_count = IMAGES_COLUMN_COUNT if len(files_list) > IMAGES_COLUMN_COUNT else len(files_list)
    return (
        (IMAGE_SIZE[0] * column_count + (BETWEEN_IMAGES_SPACE_SIZE * (column_count - 1)) + WIDTH_SPACE_SIZE),
        (IMAGE_SIZE[1] * get_strings_count(files_list) + (
                BETWEEN_IMAGES_SPACE_SIZE * (get_strings_count(files_list) - 1))) + HEIGHT_SPACE_SIZE)


def create_tif(files_list: list) -> None:
    width, height = get_size(files_list)
    with Image.new("RGB", (width, height), (255, 255, 255)) as tif:
        photo_number = 0
        for w in range(0, get_strings_count(files_list)):
            for y in range(0, IMAGES_COLUMN_COUNT):
                with Image.open(files_list[photo_number]).resize(IMAGE_SIZE) as image:
                    tif.paste(image, box=(int(WIDTH_SPACE_SIZE / 2) + (IMAGE_SIZE[0] + BETWEEN_IMAGES_SPACE_SIZE) * y,
                                          (int(HEIGHT_SPACE_SIZE / 2) + (
                                                  IMAGE_SIZE[1] + BETWEEN_IMAGES_SPACE_SIZE) * w)))

                if photo_number == len(files_list) - 1:
                    break
                else:
                    photo_number += 1

        tif.save(FILE_NAME)


def get_folders_list_from_sys_args() -> list:
    """
    Get folders from command line
    :return: list of folders
    """
    folder_list = []
    for arg in sys.argv:
        if arg != 'main.py' and arg != '' and arg != 'yandex' and (os.path.exists(arg) or os.path.exists(BASE_ZIP_DIR + arg)):
            folder_list.append(arg)
    return folder_list


if __name__ == "__main__":
    if 'yandex' in sys.argv:
        unzip_files(download_files(get_href(YANDEX_DISK_LINK)))

    folders_list = get_folders_list_from_sys_args()
    if folders_list:
        files = get_files_path(folders_list)
    else:
        files = get_files_path(['1388_12_Наклейки 3-D_3',])

    create_tif(files)
