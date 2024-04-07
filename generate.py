#!/usr/bin/env python3

from io import TextIOWrapper  # type checking
import os
import shutil
from pathlib import Path
import csv

# path to root dir. github pages serves website roots at /docs
WEBSITE_ROOT = "docs"

with (Path("templates") / "generic_webpage.html").open() as generic:
    GENERIC_WEBSITE_TEMPLATE = generic.read()


def process(s: str, input_path: str) -> str:
    output = GENERIC_WEBSITE_TEMPLATE.format(generic_webpage_CONTENT=content)

    # TODO support multiple passes: while {.*} in output, feed back into loop below?

    print("input path: " + input_path)
    if input_path == "generator/about.html":
        author_cards: list[str] = []

        with open("authors.tsv", newline="") as tsvfile:
            assert has_no_duplicate_ids(tsvfile)

            reader = csv.DictReader(tsvfile, delimiter="\t")

            for author_row in reader:
                author_cards.append(
                    f'<p><a href="/authors/{author_row["name"]}.html">{author_row["name"]}</a></p>'
                )

        output = output.format(about_AUTHORS="\n".join(author_cards))
        # TODO all this
    elif input_path == "etc etc":
        output = output

    return output


def has_no_duplicate_ids(tsvfile: TextIOWrapper) -> bool:
    """Specification function that checks if a TextIOWrapper that should point to an authors.tsv contains any duplicate author ids.
    
    Returns whether this is false and prints out any duplicates found along the way."""
    reader = csv.DictReader(tsvfile, delimiter="\t")
    ids = set()
    id_count = 0

    for author_row in reader:
        id = author_row["id"]
        if id in ids:
            print(f"duplicate id near line {id_count+2}: {id}")
        ids.add(id)
        id_count += 1

    return len(ids) == id_count


def generate_author_profiles():
    with open("authors.tsv", newline="") as tsvfile:
        assert has_no_duplicate_ids(tsvfile)
        reader = csv.DictReader(tsvfile, delimiter="\t")

        for author_row in reader:
            author_fpath = f"docs{os.sep}authors{os.sep}" + author_row["name"] + ".html"
            author_template = f"templates{os.sep}generic_author_profile.html"
            with (
                open(author_fpath, "w") as output,
                open(author_template, "r") as template,
            ):
                output.write(
                    template.read().format(
                        AuthorImage=author_row["image"],
                        AuthorImageAltText=author_row["image_alt"],
                        AuthorPronouns=author_row["pronouns"],
                        AuthorMajor=author_row["major"],
                        AuthorYear=author_row["year"],
                        AuthorLocation=author_row["location"],
                        AuthorFact=author_row["fact"],
                        AuthorEmail=author_row["email"],
                        OtherSocials=author_row["other_socials"],
                        AuthorName=author_row["name"],
                        AuthorBio=author_row["bio"],
                        AuthorPrevArticles="{AuthorPrevArticles}",
                    )
                )


for root, dirs, files in os.walk("generator"):
    generate_author_profiles()

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
