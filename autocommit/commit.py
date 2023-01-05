from __future__ import print_function, unicode_literals
from PyInquirer import prompt as py_inquirer_prompt, style_from_dict, Token
import subprocess

import keyring

import os
import re
import markdown

from pydantic import BaseModel
from langchain.llms import OpenAI
from langchain.prompts import BasePromptTemplate
from dotenv import load_dotenv

load_dotenv()

OPENAI_KEY = os.getenv("OPENAI_KEY")


class CustomPromptTemplate(BasePromptTemplate, BaseModel):
    template: str

    def format(self, **kwargs) -> str:
        c_kwargs = {k: v for k, v in kwargs.items()}
        return self.template.format(**c_kwargs)


prompt = CustomPromptTemplate(
    input_variables=["diff"],
    template="""
    What follows "-------" is a git diff for a potential commit.
    Reply with a markdown unordered list of 5 possible, different Git commit messages 
    (a Git commit message should be concise but also try to describe 
    the important changes in the commit), order the list by what you think 
    would be the best commit message first, and don't include any other text 
    but the 5 messages in your response.
    ------- 
    {diff}
    -------
""",
)


def generate_suggestions(diff, openai_api_key=OPENAI_KEY):

    llm = OpenAI(
        temperature=0.2,
        openai_api_key=openai_api_key,
        max_tokens=100,
        model_name="text-davinci-003",
    )  # type: ignore

    # query OpenAI
    formattedPrompt = prompt.format(diff=diff)
    response = llm(formattedPrompt)

    # Convert the markdown string to HTML
    html = markdown.markdown(response)

    # Use a regular expression to extract the list items from the HTML
    items = re.findall(r"<li>(.*?)</li>", html)
    return items


SERVICE_ID = "auto-commit-cli"


def prompt_for_openai_api_key():
    questions = [
        {
            "type": "input",
            "name": "openai_api_key",
            "message": "Please enter your OpenAI API key:",
        }
    ]
    answers = py_inquirer_prompt(questions)
    openai_api_key = answers["openai_api_key"]
    keyring.set_password(SERVICE_ID, "user", openai_api_key)
    return openai_api_key


def main():
    # Prompt for OpenAI API key if it's not set
    openai_api_key = keyring.get_password(SERVICE_ID, "user")
    if openai_api_key is None:
        openai_api_key = prompt_for_openai_api_key()

    #  Get the diff including untracked files (see https://stackoverflow.com/a/52093887)
    git_command = "git --no-pager diff; for next in $( git ls-files --others --exclude-standard ) ; do git --no-pager diff --no-index /dev/null $next; done;"

    # Windows support
    if os.name == "nt":
        git_command = """git diff && for /f "delims=" %a in ('git ls-files --others --exclude-standard') do (git diff --no-index /dev/null %a)"""

    output = subprocess.run(
        git_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    if len(output.stderr) > 0:
        error = output.stderr.decode("utf-8")
        print("There was an error retrieving the current diff: ")
        if error.startswith("warning: Not a git repository"):
            print("You're not inside a git repo. Please run it from inside a git repo.")
        else:
            print(error)
        exit(-1)

    diff = output.stdout.decode("utf8")
    # Trim the diff
    diff = diff.strip()

    if len(diff) == 0:
        print("Diff is empty. Nothing to commit.")
        exit(0)

    suggestions = []

    try:
        suggestions = generate_suggestions(diff[:7000], openai_api_key=openai_api_key)
    except Exception as e:
        print("There was an error generating suggestions from OpenAI: ")
        # Prompt for OpenAI API key if it's incorrect
        if "Incorrect API key provided" in str(e):
            openai_api_key = prompt_for_openai_api_key()
            print("Please re-run the command now.")
        else:
            print(e)
        exit(-1)

    if len(suggestions) == 0:
        print("No suggestions found.")
        exit(0)

    # Prompt user with commit messages and choices and allow edits
    custom_style = style_from_dict(
        {
            Token.Separator: "#6C6C6C",
            Token.QuestionMark: "#000000",
            Token.Selected: "#FFFF00 bold",
            Token.Pointer: "#FF9D00 bold",
            Token.Instruction: "",
            Token.Answer: "#EA9104 bold",
            Token.Question: "",
        }
    )

    questions = [
        {
            "type": "list",
            "name": "commit_message",
            "message": "Commit message suggestions:",
            "choices": [f"{i + 1}. {item}" for i, item in enumerate(suggestions)],
            "filter": lambda val: val[3:],
        }
    ]
    answers = py_inquirer_prompt(questions, style=custom_style)
    answers = py_inquirer_prompt(
        [
            {
                "type": "input",
                "name": "final_commit_message",
                "message": "Confirm or edit the commit message:",
                "default": answers.get("commit_message"),
            },
        ]
    )

    # Commit the changes
    git_command = (
        'git add -A; git commit -m "' + answers.get("final_commit_message") + '"'
    )

    # Windows support
    if os.name == "nt":
        git_command = (
            'git add -A && git commit -m "' + answers.get("final_commit_message") + '"'
        )

    output = subprocess.run(
        git_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    if len(output.stderr) > 0:
        error = output.stderr.decode("utf-8")
        print("There was an error committing:")
        print(error)
    else:
        print("Commit successful with message:", answers.get("final_commit_message"))


if __name__ == "__main__":
    main()
