import sys
import pandas as pd

NEW_AUTHORS_PATH = sys.argv[1]

print(NEW_AUTHORS_PATH)
authors_df = pd.read_csv(NEW_AUTHORS_PATH, sep="\t", header=0, dtype=str)
cols = authors_df.columns.tolist()
print(f"COLS: {cols}")
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
print(f"COLS AFTER: {new_cols}")
authors_df = authors_df[new_cols]

print(f"new df: {authors_df}")
print(f"double checking cols: {authors_df.columns.tolist()}")

authors_df.insert(0, "id", "TODO")
authors_df.insert(3, "image_alt", "TODO")
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

print(f"new df: {authors_df}")
authors_df.to_csv("out.csv", sep="\t", index=False)
