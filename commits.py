from collections import namedtuple
import os
import shutil
import csv
import sys
import git
import pygit2
from langchain.llms import OpenAI
from langchain.prompts import BasePromptTemplate
from pydantic import BaseModel
import re
import markdown
from dotenv import load_dotenv

load_dotenv()

# TODO: Revoke key
OPENAI_KEY = os.getenv("OPENAI_KEY")

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


class CustomPromptTemplate(BasePromptTemplate, BaseModel):
    template: str

    def format(self, **kwargs) -> str:
        c_kwargs = {k: v for k, v in kwargs.items()}
        return self.template.format(**c_kwargs)


prompt = CustomPromptTemplate(
    input_variables=["diff"], template="""
    What follows "-------" is a git diff for a potential commit.
    Reply with a markdown unordered list of 5 possible, different Git commit messages 
    (a Git commit message should be concise but also try to describe 
    the important changes in the commit), order the list by what you think 
    would be the best commit message first, and don't include any other text 
    but the 5 messages in your response.
    ------- 
    {diff}
    -------
""")

llm = OpenAI(temperature=0.2, openai_api_key=OPENAI_KEY,
             max_tokens=100, model_name="text-davinci-003")

filtered_commit_objects = commit_objects[:5]

writer = csv.writer(sys.stdout, quoting=csv.QUOTE_MINIMAL)

for commit in filtered_commit_objects:
    message = commit.message.replace("\n", ";")

    # Skip merge commits
    if message.startswith("Merge"):
        continue

    # print(commit.diff)
    # print(prompt.format(diff=commit.diff))

    # text-davinci-003 supports 4000 tokens. Let's use upto 3500 tokens for the prompt.
    # 3500 tokens = 14,000 characters (https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them)
    # We're using the first 14000 characters of the diff
    response = llm(prompt.format(diff=commit.diff[:14000]))

    # Convert the markdown string to HTML
    html = markdown.markdown(response)
    # Use a regular expression to extract the list items from the HTML
    items = re.findall(r'<li>(.*?)</li>', html)

    # generate CSV row
    for item in items:
        if item == items[0]:
            writer.writerow([commit.sha, message, item])
        else:
            writer.writerow(['', '', item])

    # print("-----")
