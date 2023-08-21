import json
import logging as log
import os
import random
import re
import time
import uuid
from datetime import datetime
from difflib import SequenceMatcher
from os import environ
from pathlib import Path
import pytz

from pdf2image import convert_from_path
from PIL import Image
# from PyPDF2 import PdfReader
from pypdf import PdfReader
from src.utils.export import export_file
from src.utils.export import json_to_text

IMAGE_PREFIX = environ.get("IMAGE_PREFIX", ".")
TIMEZONE = pytz.timezone("Europe/Lisbon")
##################################################
# FILESYSTEM UTILS
##################################################

# Current file system structure
# files
# - folder1
#   - filename.(pdf/png/jpg/...)
#       - filename.(pdf/png/jpg/...)    (the original submitted file)
#       - filename_extracted.txt        (the text extracted initially)
#       - filename_changes.txt          (the text changed by the user)
#       - conf.txt                      (the conf file of the OCR engine used)
# - folder2

# DONE
def get_current_time():
    """
    Get the current time in the correct format

    :return: current time
    """
    return datetime.now().astimezone(TIMEZONE).strftime("%d/%m/%Y %H:%M:%S")

# TODO
def get_file_parsed(path):
    """
    Return the text off all the pages of the file

    :param path: path to the file
    :return: list with the text of each page
    """
    path += "/ocr_results"
    files = [
        f"{path}/{f}"
        for f in os.listdir(path)
        if os.path.isfile(os.path.join(path, f))
        and ".json" in f
        and "_data.json" not in f
    ]

    data = []
    for file in files:
        basename = get_file_basename(file)
        with open(file, encoding="utf-8") as f:
            hocr = json.load(f)

            data.append(
                {
                    "original_file": file,
                    "content": hocr,
                    "page_url": IMAGE_PREFIX
                    + "/images/"
                    + "/".join(file.split("/")[1:-2])
                    + "/"
                    + basename
                    + ".jpg",
                }
            )
    return data

# TODO
def get_file_layouts(path):
    layouts = []
    basename = get_file_basename(path)
    data = get_data(f"{path}/_data.json")

    for page in range(data["pages"]):
        filename = f"{path}/layouts/{basename}_{page}.json"
        page_url = IMAGE_PREFIX + "/images/" + "/".join(path.split("/")[1:]) + f"/{basename}_{page}.jpg"

        if os.path.exists(filename):
            with open(filename, encoding="utf-8") as f:
                layouts.append({
                    "boxes": json.load(f),
                    "page_url": page_url
                })
        else:
            layouts.append({
                "boxes": [],
                "page_url": page_url
            })

    return layouts

# TODO
def save_file_layouts(path, layouts):
    basename = get_file_basename(path)
    if not os.path.isdir(f"{path}/layouts"):
        os.mkdir(f"{path}/layouts")

    for id, page in enumerate(layouts):
        layouts = page["boxes"]
        filename = f"{path}/layouts/{basename}_{id}.json"

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(layouts, f, indent=2)
  
# DONE
def generate_uuid(path):
    random.seed(path)
    return str(
        uuid.UUID(bytes=bytes(random.getrandbits(8) for _ in range(16)), version=4)
    )

# TODO
def delete_structure(client, path):
    """
    Delete all the files in the structure
    """
    data = get_data(path + "/_data.json")
    if data["type"] == "file":
        if data.get("indexed", False):
            files = [f"{path}/{f}" for f in os.listdir(path) if f.endswith(".txt")]
            for file in files:
                id = generate_uuid(file)
                client.delete_document(id)

    else:
        folders = [
            f"{path}/{f}" for f in os.listdir(path) if os.path.isdir(f"{path}/{f}")
        ]
        for folder in folders:
            delete_structure(client, folder)

# TODO
def get_filesystem(path):
    """
        @@ -106,7 +101,7 @@ def get_filesystem(path):
    @param path: path to the folder
    """
    files = get_structure(path)
    info = get_structure_info(path)

    if files is None:
        files = {path: []}


    return {**files, "info": info}

# TODO
def get_creation_time(path):
    """
    Get the creation time of the file/folder

    :param path: path to the file/folder
    :return: creation time
    """

    ti_c = os.path.getctime(path)
    c_ti = time.ctime(ti_c)
    t_obj = time.strptime(c_ti)
    c_time = time.strftime("%Y-%m-%d %H:%M:%S", t_obj)
    return c_time

# TODO
def get_modification_time(path):
    """
    Get the modification time of the file/folder

    :param path: path to the file/folder
    :return: modification time
    """

    ti_m = os.path.getmtime(path)
    m_ti = time.ctime(ti_m)
    t_obj = time.strptime(m_ti)
    m_time = time.strftime("%Y-%m-%d %H:%M:%S", t_obj)
    return m_time

# TODO
def get_ocr_size(path):
    """
    Get the size of the hocr files

    :param path: path to the folder
    :return: size of the files
    """

    files = [
        f"{path}/{f}"
        for f in os.listdir(path)
        if os.path.isfile(os.path.join(path, f)) and ".json" in f
    ]
    size = 0
    for file in files:
        size += os.path.getsize(file)

    if size < 1024:
        return f"{size} B"
    elif size < 1024**2:
        return f"{size / 1024:.2f} KB"
    elif size < 1024**3:
        return f"{size / 1024 ** 2:.2f} MB"
    else:
        return f"{size / 1024 ** 3:.2f} GB"

# TODO
def get_size(path, path_complete=False):
    """
    Get the size of the file

    :param path: path to the file
    :return: size of the file
    """

    name = path.split("/")[-1]
    if not path_complete:
        path = f"{path}/{name}"

    size = os.path.getsize(path)

    if size < 1024:
        return f"{size} B"
    elif size < 1024**2:
        return f"{size / 1024:.2f} KB"
    elif size < 1024**3:
        return f"{size / 1024 ** 2:.2f} MB"
    else:
        return f"{size / 1024 ** 3:.2f} GB"

# TODO
def get_folder_info(path):
    """
    Get the info of the folder
    :param path: path to the folder
    """
    info = {}
    data = get_data(f"{path}/_data.json")
    if "type" not in data:
        return {}

    if data["type"] == "file" and ("progress" not in data or data["progress"] == True):
        data["size"] = get_size(path)

    info[path] = data
    return info

# TODO
def get_structure_info(path):
    """
    Get the info of each file/folder
    @param files: the filesystem structure
    """
    info = {}

    for root, folders, _ in os.walk(path):
        for folder in folders:
            folder_path = f"{root}/{folder}".replace("\\", "/")

            folder_info = get_folder_info(folder_path)

            info = {**info, **folder_info}

    return info

# TODO
def get_structure(path):
    """
    Put the file system structure in a dict
    {
        'files': [
            {
                'folder1': ['file.pdf']
            },
            {
                'folder2': []
            }
        ]
    }

    :param path: the path to the files
    """
    filesystem = {}
    name = path.split("/")[-1]

    if path != name:
        data = get_data(f"{path}/_data.json")
        if "type" not in data:
            return None
        if data["type"] == "file":
            return name

    contents = []
    folders = sorted([f for f in os.listdir(path) if os.path.isdir(f"{path}/{f}")])
    for folder in folders:
        file = get_structure(f"{path}/{folder}")
        if file is not None:
            contents.append(file)

    filesystem[name] = contents
    return filesystem

##################################################
# FILES UTILS
##################################################
# DONE
def get_page_count(filename):
    """
    Get the number of pages of a file
    """

    extension = filename.split(".")[-1]
    if extension == "pdf":
        with open(filename, "rb") as f:
            return len(PdfReader(f).pages)
    elif extension in ["jpg", "jpeg"]:
        return 1

# DONE
def get_file_basename(filename):
    """
    Get the basename of a file

    :param file: file name
    :return: basename of the file
    """
    return ".".join(filename.split("/")[-1].split(".")[:-1])

# DONE
def get_file_extension(filename):
    """
    Get the extension of a file

    :param file: file name
    :return: extension of the file
    """
    return filename.split(".")[-1]

##################################################
# OCR UTILS
##################################################
# TODO
def get_data(file):
    if not os.path.exists(file): return {}
    with open(file, encoding="utf-8") as f:
        text = f.read()
        if text == "":
            return {}
        return json.loads(text)

# TODO
def update_data(file, data):
    """
    Update the data file
    @param file: path to the data file
    @param data: data to update
    """

    previous_data = get_data(file)
    with open(file, "w", encoding="utf-8") as f:
        previous_data.update(data)
        json.dump(previous_data, f)

# TODO
def prepare_file_ocr(path):
    """
    Prepare the OCR of a file
    @param path: path to the file
    @param ocr_folder: folder to save the results
    """
    try:
        extension = path.split(".")[-1]
        basename = get_file_basename(path)

        log.info("{path}: A preparar páginas")

        if extension == "pdf":
            pages = convert_from_path(
                f"{path}/{basename}.pdf",
                paths_only=True,
                output_folder=path,
                fmt="jpg",
                thread_count=2,
            )
            log.info("{path}: A trocar os nomes das páginas")
            for i, page in enumerate(pages):
                if os.path.exists(f"{path}/{basename}_{i}.jpg"):
                    os.remove(page)
                else:
                    Path(page).rename(f"{path}/{basename}_{i}.jpg")

        elif extension in ["jpeg", "jpg"]:
            img = Image.open(f"{path}/{basename}.{extension}")
            img.save(f"{path}/{basename}.jpg", "JPEG")
    except Exception as e:
        data_folder = f"{path}/_data.json"
        data = get_data(data_folder)
        data["ocr"]["exceptions"] = str(e)
        update_data(data_folder, data)
        log.error(f"Error in preparing OCR for file at {path}: {e}")

# TODO
def similarity_score(text1, text2):
    """
    Compute the similarity score between two texts

    :param text1: first text
    :param text2: second text
    :return: similarity score
    """
    return SequenceMatcher(None, text1, text2).ratio()

# TODO
def fix_ocr(previous_words, current_text):
    """
    Update the hOCR results with the current submitted text

    :param previous_words: previous words removed from the hOCR results - [["Tnis", ...], ...]
    :param current_text: current text - "This ..."
    :return: updated hOCR results
    """

    current_words = [[w for w in l.split()] for l in current_text.split("\n")]

    for line_id, previous_line in enumerate(previous_words):
        current_line = current_words[line_id]

        # I'm not expecting tesseract to insert spaces where there is none
        # But could be wrong
        if len(current_line) < len(previous_line):
            raise ValueError(
                "The current text is shorter than the previous one, not expecting that"
            )

        pp, pc = 0, 0  # previous and current position
        while pc < len(current_line) and pp < len(previous_line):
            current_diff = pp - pc

            if current_diff == len(previous_line) - len(current_line):
                # We can't attemp to join any words. Every current word should match the previous one
                same_score, adding_score = 1, 0
            else:
                same_score = similarity_score(current_line[pc], previous_line[pp])
                adding_score = similarity_score(
                    "".join(current_line[pc : pc + 2]), previous_line[pp]
                )

            if same_score >= adding_score:
                previous_line[pp] = current_line[pc]
                pc += 1
                pp += 1
            else:
                previous_line[pp] = " ".join(current_line[pc : pc + 2])
                pp += 1
                pc += 2

    return previous_words
