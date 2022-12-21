from __future__ import print_function, unicode_literals
from PyInquirer import prompt as py_inquirer_prompt, style_from_dict, Token
import subprocess

from llm import generate_suggestions


def main():
    #  Get the diff including untracked files (see https://stackoverflow.com/a/52093887)
    git_command = "git --no-pager diff; for next in $( git ls-files --others --exclude-standard ) ; do git --no-pager diff --no-index /dev/null $next; done;"
    output = subprocess.run(git_command, shell=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

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

    suggestions = generate_suggestions(diff)

    if len(suggestions) == 0:
        print("No suggestions found.")
        exit(0)

    # Prompt user with commit messages and choices and allow edits
    custom_style = style_from_dict({
        Token.Separator: '#6C6C6C',
        Token.QuestionMark: '#000000',
        Token.Selected: '#FFFF00 bold',
        Token.Pointer: '#FF9D00 bold',
        Token.Instruction: '',
        Token.Answer: '#EA9104 bold',
        Token.Question: '',
    })

    questions = [
        {
            'type': 'list',
            'name': 'commit_message',
            'message': 'Commit message suggestions:',
            'choices': [f"{i + 1}. {item}" for i, item in enumerate(suggestions)],
        }
    ]
    answers = py_inquirer_prompt(questions, style=custom_style)
    answers = py_inquirer_prompt([{
        'type': 'input',
        'name': 'final_commit_message',
        'message': 'Confirm or edit the commit message:',
        'default': answers.get('commit_message')
    }, ])

    # Commit the changes
    git_command = "git add -A; git commit -m \"" + \
        answers.get('final_commit_message') + "\""
    output = subprocess.run(git_command, shell=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if len(output.stderr) > 0:
        error = output.stderr.decode("utf-8")
        print("There was an error committing: ")
        print(error)
    else:
        print("Commit successful with message: ",
              answers.get('final_commit_message'))


if __name__ == "__main__":
    main()
