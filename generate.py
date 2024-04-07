#!/usr/bin/env python3

import os
import shutil
from pathlib import Path
import pandas as pd

# path to root dir. github pages serves website roots at /docs
WEBSITE_ROOT = "docs"

with (Path("templates") / "generic_webpage.html").open() as generic:
    GENERIC_WEBSITE_TEMPLATE = generic.read()


def process(s: str, input_path: str) -> str:
    output = GENERIC_WEBSITE_TEMPLATE.format(generic_webpage_CONTENT=content)

    # TODO support multiple passes: while {.*} in output, feed back into loop below

    print("input path: " + input_path)
    if input_path == "generator/about.html":
        author_cards: list[str] = []

        authors_df = pd.read_csv("authors.tsv", sep='\t', header=0)
        print(authors_df)
        output = output.format(about_AUTHORS=author_cards)
        # TODO all this
    elif input_path == "etc etc":
        output = output
    
    return output


for root, dirs, files in os.walk("generator"):
    for filename in files:
        # the dir fstring takes our walk and spits out which dir the current file lives in.
        # eg, a file at "generator/assets/images/img.png" turns to "{WEBSITE_ROOT}/assets/images/img.png"
        dir = f"{WEBSITE_ROOT}{os.sep}{os.sep.join(root.split(os.sep, maxsplit=1)[1:])}"
        
        # create any dirs that need to be created in order to write to our file
        os.makedirs(dir, exist_ok=True)

        INPUT_PATH = os.path.join(root, filename)
        OUTPUT_PATH = os.path.join(dir, filename)
        print(f"processing {INPUT_PATH} to {OUTPUT_PATH}")

        if filename[-5:] != ".html":
            shutil.copyfile(INPUT_PATH, OUTPUT_PATH)
            continue

        with (
            open(INPUT_PATH, "r") as f_in,
            open(OUTPUT_PATH, "w") as f_out,
        ):
            content = f_in.read()
            output = process(content, INPUT_PATH)
            f_out.write(output)
