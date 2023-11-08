import os
from os.path import join as path_join

PATH = "/mnt/c/users/admin/downloads"
PATH_EXT = False

EXT_MAPPER = {
    # Images
    "jpeg": "image",
    "jpg": "image",
    "gif": "image",
    "jfif": "image",
    "bmp": "image",
    "png": "image",
    "webp": "image",
    "heic": "image",
    "heif": "image",
    "svg": "image",
    "ico": "image",
    "tiff": "image",
    "tif": "image",

    # Videos
    "mov":"video",
    "mp4":"video",
    "mkv":"video",
    "webm":"video",
    "flv":"video",

    # Audios
    "ogg":"audio",
    "mp3":"audio",
    "flac":"audio",
    "opus":"audio",
    "wav":"audio",
    "aiff":"audio",
    "m3u":"audio",
    "m3u8":"audio",
    "mid":"audio",
    "opus":"audio",


    # Ebooks
    "epub": "ebook",
    "mobi": "ebook",
    "azw3": "ebook",
    "cbz": "ebook",
    "cbr": "ebook",

    # PDF    
    "pdf": "pdf",

    # Compactados
    "zip": "compacted",
    "rar": "compacted",
    "tar": "compacted",
    "tar.gz": "compacted",
    "7z": "compacted",


    # Office 
    "ppt": "office",
    "pptx": "office",
    "xls": "office",
    "xlsx": "office",
    "doc": "office",
    "docx": "office",
    "odb":"office",
    "odf":"office",
    "odp":"office",
    "ods":"office",
    "odg":"office",
    "ods":"office",
    "odt":"office",

    # Text
    "md": "text",
    "txt": "text",
    "html": "text",
    "rtf": "text",
    "csv": "text",
    "json": "text",
    "xhtml": "text",
    "tsv": "text",
    "yml": "text",
    "yaml": "text",
    
    # Source
    "c": "source",
    "c++": "source",
    "cpp": "source",
    "aspx": "source",
    "b": "source",
    "bat": "source",
    "asm": "source",
    "bin": "source",
    "apk": "source",
    "cbl": "source",
    "cc": "source",
    "class": "source",
    "cmd": "source",
    "cs": "source",
    "csproj": "source",
    "css": "source",
    "dat":"source",
    "f":"source",
    "go":"source",
    "mod":"source",
    "h":"source",
    "h++":"source",
    "hh":"source",
    "hpp":"source",
    "iso":"source",
    "jar":"source",
    "json":"source",
    "js":"source",
    "java":"source",
    "kt":"source",
    "o":"source",
    "php":"source",
    "pkl":"source",
    "rs":"source",
    "sass":"source",
    "db":"source",
    "sql":"source",
    "ts":"source",
    "tsx":"source",
    "jsx":"source",
    "exe":"source",

    # Fallback value
    "*": "misc"
}

FOLDERS = set(EXT_MAPPER.values())

def assert_path(path):
    if not os.path.isdir(path):
        os.mkdir(path)

for blob in os.listdir(PATH):
    if os.path.isdir(path_join(PATH, blob)):
        if blob not in FOLDERS:
            print(blob, "-> folder")
            assert_path(path_join(PATH, "folder"))
            os.rename(path_join(PATH, blob), path_join(PATH, "folder", blob))
        continue
    else: 
        ext = blob.split(".")[-1].lower()
        print(blob, "->",  ext)
        if ext in EXT_MAPPER:
            assert_path(path_join(PATH, EXT_MAPPER[ext]))
            os.rename(path_join(PATH, blob), path_join(PATH, EXT_MAPPER[ext], blob))
        else:
            assert_path(path_join(PATH, EXT_MAPPER["*"]))
            os.rename(path_join(PATH, blob), path_join(PATH, EXT_MAPPER["*"], blob))

input()