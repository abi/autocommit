from collections import namedtuple
import os
import shutil
import csv
import sys
from dotenv import load_dotenv
import git
import pygit2

from autocommit.llm import generate_suggestions

load_dotenv()

GIT_REPO_URL = os.getenv("GIT_REPO_URL")
if GIT_REPO_URL is None:
    raise ValueError("GIT_REPO_URL is not set")

temp_repo_dir = "/tmp/ai-commit-msg-repo"

# Delete the directory if it exists
if os.path.exists(temp_repo_dir):
    shutil.rmtree(temp_repo_dir)

# Clone the repository
git.Repo.clone_from(GIT_REPO_URL, temp_repo_dir)

# Open the repository
repo = pygit2.Repository(temp_repo_dir)
commits = repo.walk(repo.head.target, pygit2.GIT_SORT_TIME)

# Iterate over the commits and organize the data we need
commit_objects = []
CommitObject = namedtuple("CommitObject", ["sha", "message", "diff"])
for commit in commits:
    if len(commit.parents) > 0:
        diff = repo.diff(commit.parents[0], commit).patch
    else:
        diff = ""
    commit_objects.append(CommitObject(commit.id, commit.message, diff))

filtered_commit_objects = commit_objects

writer = csv.writer(sys.stdout, quoting=csv.QUOTE_MINIMAL)

for commit in filtered_commit_objects:
    message = commit.message.replace("\n", ";")

    # Skip merge commits
    if message.startswith("Merge"):
        continue

    # text-davinci-003 supports 4000 tokens. Let's use upto 3500 tokens for the prompt.
    # 3500 tokens = 14,000 characters (https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them)
    # But in practice, > 7000 seems to exceed the limit
    suggestions = generate_suggestions(commit.diff[:7000])

    # generate CSV row
    for item in suggestions:
        # Only inlude SHA & original message for the first row
        if item == suggestions[0]:
            writer.writerow([commit.sha, message, item])
        else:
            writer.writerow(["", "", item])
