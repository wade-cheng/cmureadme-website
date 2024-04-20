import zipfile
import toml 
import os
import sys
import shutil
import glob
# shutil.unpack_archive(filename, extract_dir)

"""takes a downloaded article (either an image or Google Docs zipped HTML) and adds it to the repo.
use via `python3 add_article.py ~/example/path/to/article.zip`
"""

# os.makedirs(dir, exist_ok=True)

NEW_ARTICLE_PATH = sys.argv[1]
print(f"new was {NEW_ARTICLE_PATH}")

ACCEPTED_FILE_FORMATS = {"jpg", "png", "zip"}
assert NEW_ARTICLE_PATH.split(".")[-1] in ACCEPTED_FILE_FORMATS

toml_dict = dict()

toml_dict["title"] = input("article title > ")
toml_dict["type"] = "article" if NEW_ARTICLE_PATH.split(".")[-1] == "zip" else "art"
toml_dict["author"] = input("article author id > ")
toml_dict["issue"] = input("article issue number > ")
toml_dict["date"] = input("article date > ")
toml_dict["description"] = input("article description blurb > ")

def format_filename(s: str) -> str:
    s = s.lower()
    return "".join([c for c in s if c in "abcdefghijklmnopqrstuvwxyz0123456789"])

ARCHIVE_PATH = f"articles{os.sep}issue_{toml_dict['issue'].zfill(3)}{os.sep}{format_filename(toml_dict['title'])}"

os.makedirs(ARCHIVE_PATH, exist_ok=True)

if toml_dict["type"] == "article":
    """if we're operating on a zip file google docs export"""
    with zipfile.ZipFile(NEW_ARTICLE_PATH, 'r') as zip_ref:
        zip_ref.extractall(ARCHIVE_PATH)
    toml_dict["path"] = os.path.basename(glob.glob(ARCHIVE_PATH + os.sep + "*.html")[0])
elif toml_dict["type"] == "art":
    shutil.copyfile(src=NEW_ARTICLE_PATH, dst=ARCHIVE_PATH+os.sep+os.path.basename(NEW_ARTICLE_PATH))
    toml_dict["path"] = os.path.basename(NEW_ARTICLE_PATH)
else:
    print("what in the world")
    exit()



with open(ARCHIVE_PATH + f"{os.sep}metadata.toml", "w") as f:
    toml.dump(toml_dict, f)