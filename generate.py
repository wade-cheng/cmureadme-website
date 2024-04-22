#!/usr/bin/env python3

import toml
import glob
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

        assert no_dupe_author_ids()
        with open("authors.tsv", newline="") as tsvfile:

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


def no_dupe_author_ids() -> bool:
    """Specification function that checks if authors.tsv contains any duplicate author ids.

    Returns whether this is false and prints out any duplicates found along the way."""
    # note: taking in the TextIOWrapper as a parameter instead seems to "consume" the TextIOWrapper? weird.
    with open("authors.tsv", newline="") as tsvfile:
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
    assert no_dupe_author_ids()
    with open("authors.tsv", newline="") as tsvfile:
        reader = csv.DictReader(tsvfile, delimiter="\t")

        for author_row in reader:
            # we fill authors_id_names
            authors_id_names[author_row["id"]] = author_row["name"]

            author_fpath = f"docs{os.sep}authors{os.sep}" + author_row["name"] + ".html"
            author_template = f"templates{os.sep}generic_author_profile.html"
            webpage_template = f"templates{os.sep}generic_webpage.html"
            with (
                open(author_fpath, "w") as output,
                open(author_template, "r") as author_template,
                open(webpage_template, "r") as webpage_template,
            ):
                output.write(
                    webpage_template.read()
                    .format(generic_webpage_CONTENT=author_template.read())
                    .format(
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
                    .format(AuthorPrevArticles="TEMP")
                )


def generate_articles():
    # reset past articles webpage first
    with open(f"generator{os.sep}past.html", "w") as f:
        f.write("")

    for article_path in glob.glob(f"articles{os.sep}*{os.sep}*"):
        article_meta_path = article_path + os.sep + "metadata.toml"

        with open(article_meta_path, "r") as t:
            article_metadata = toml.loads(t.read())
            
        # fill out `articles` variable (below)
        # TODO (also this breaks if any invariant is wrong such as ids in tomls being misplaced.)
        if article_metadata["author"] not in articles:
            articles[article_metadata["author"]] = []
        articles[article_metadata["author"]].append(article_path)

        # generate
        if article_metadata["type"] == "article":
            docs_path = "docs" + os.sep + article_path
            os.makedirs(docs_path, exist_ok=True)
            shutil.copytree(article_path, docs_path, dirs_exist_ok=True)

            with open(article_path + os.sep + article_metadata["path"], "r") as f:
                html_content = f.read()
            with (
                open(f"templates{os.sep}generic_article.html") as article,
                open(f"templates{os.sep}generic_webpage.html") as webpage,
                open(docs_path + os.sep + article_metadata["path"], "r") as read_f,
            ):
                
                article_formatted = webpage.read().format(generic_webpage_CONTENT=article.read())
                # print(article_formatted)
                article_formatted = article_formatted.replace("{articleCategory}", "temp")
                article_formatted = article_formatted.replace("{articleTitle}", "temp")
                article_formatted = article_formatted.replace("{articlePublishDate}", "temp")
                article_formatted = article_formatted.replace("{articleSummary}", "temp")
                article_formatted = article_formatted.replace("{articleAuthor}", "temp")
                article_formatted = article_formatted.replace("{articleThumbnailUrl}", "temp")
                article_formatted = article_formatted.replace("{articleThumbnailAltText}", "temp")
                article_formatted = article_formatted.replace("{articleBody}", read_f.read())
                article_formatted = article_formatted.replace("max-width:468pt;", "")  # not sure why this is here but i'm fairly sure it comes from the google drive html export
            with open(docs_path + os.sep + article_metadata["path"], "w") as write_f:
                write_f.write(article_formatted)
            os.remove(f"docs{os.sep}{article_meta_path}")

            with open(f"generator{os.sep}past.html", "a") as past:
                past.write(f"<a href='{article_path + os.sep + article_metadata['path']}'>{article_path + os.sep + article_metadata['path']}</a><br>")
        elif article_metadata["type"] == "art":
            print("TODO ART IS NOT IMPLEMENTED")
            pass


# a hashmap from author ids to author names
authors_id_names: dict[str, str] = dict()  # TODO FILL THIS
generate_author_profiles()

# a hashmap from article author ids to the paths of articles they've written (eg ["articles/issue_001/scottygame"])
articles: dict[str, list[str]] = dict()
generate_articles()
print(f"got articles: {articles}")

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
