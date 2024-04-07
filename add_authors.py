"""
takes downloaded .tsv from google sheets
and appends a formatted thing to `./authors.tsv`

use via 
`python3 add_authors.py ~/example/path/to/googlesheets/output.tsv`
"""

import hashlib
import sys
import pandas as pd

NEW_AUTHORS_PATH = sys.argv[1]

# print(NEW_AUTHORS_PATH)
authors_df = pd.read_csv(NEW_AUTHORS_PATH, sep="\t", header=0, dtype=str)
cols = authors_df.columns.tolist()
# print(f"COLS: {cols}")
#       0    1    2        3   4     5    6        7    8     9       10
# have: time name pronouns bio major year location fact email socials pfp
# want: id name pfp image_alt pronouns major year location fact email socials bio
cols[0] = "id"
new_cols = [
    #    "id",
    cols[1],
    cols[10],
    #    "image_alt",
    cols[2],
    cols[4],
    cols[5],
    cols[6],
    cols[7],
    cols[8],
    cols[9],
    cols[3],
]
# print(f"COLS AFTER: {new_cols}")
authors_df = authors_df[new_cols]

# print(f"new df: {authors_df}")
# print(f"double checking cols: {authors_df.columns.tolist()}")

authors_df.insert(0, "id", "TEMP")
authors_df.insert(3, "image_alt", "TEMP")
authors_df.columns = [
    "id",
    "name",
    "image",
    "image_alt",
    "pronouns",
    "major",
    "year",
    "location",
    "fact",
    "email",
    "other_socials",
    "bio",
]

def hash_string(s: str) -> str:
    # Encode the input string to bytes
    input_bytes = s.encode()

    # Create a sha1
    #  hash object
    hash_object = hashlib.sha1()

    # Update the hash object with the bytes to hash
    hash_object.update(input_bytes)

    # Get the hexadecimal representation of the digest
    hex_dig = hash_object.hexdigest()

    return hex_dig

def get_id(row):
    return hash_string(row["name"] + row["image"] + row["bio"])
authors_df["id"] = authors_df.apply(get_id, axis=1)
authors_df["image"] = "IMAGE_TEMP"

def get_image_alt(row):
    return "cover image of " + row["name"]
authors_df["image_alt"] = authors_df.apply(get_image_alt, axis=1)



# print(f"new df: {authors_df}")
output = authors_df.to_csv(sep="\t", index=False)

print("output:")
print(output)

with open("authors.tsv", "a") as f:
    f.write(output.split("\n", 1)[1])