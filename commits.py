from collections import namedtuple
import os
import shutil
import git
import pygit2

# TODO: Revoke key
OPENAI_KEY = "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"

github_repo_url = 'https://github.com/abi/codeGPT.git'
temp_repo_dir = '/tmp/ai-commit-msg-repo'

# Delete the directory if it exists
if os.path.exists(temp_repo_dir):
    shutil.rmtree(temp_repo_dir)

# Clone the repository
git.Repo.clone_from(github_repo_url, temp_repo_dir)

# Open the repository
repo = pygit2.Repository(temp_repo_dir)

# Store the data we need for each commit
CommitObject = namedtuple('CommitObject', ['sha', 'message', 'diff'])
commit_objects = []

commits = repo.walk(repo.head.target, pygit2.GIT_SORT_TIME)

# Iterate over the commits and get the data
for commit in commits:
    if len(commit.parents) > 0:
        diff = repo.diff(commit.parents[0], commit).patch
    else:
        diff = ""
    commit_objects.append(CommitObject(commit.id, commit.message, diff))

for commit in commit_objects[:1]:
    # print(commit.sha, commit.message)
    print(commit.diff)
