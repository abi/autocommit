import subprocess
import pygit2

from llm import generate_suggestions

# repo = pygit2.Repository(".")

#  Get the diff including untracked files (see https://stackoverflow.com/a/52093887)
git_command = "git --no-pager diff; for next in $( git ls-files --others --exclude-standard ) ; do git --no-pager diff --no-index /dev/null $next; done;"
output = subprocess.run(git_command, shell=True,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)

if len(output.stderr) > 0:
    error = output.stderr.decode("utf-8")
    print("There was an error running the command: ")
    if error.startswith("warning: Not a git repository"):
        print("You're not inside a git repo. Please run it from inside a git repo.")
    else:
        print(error)
    exit(-1)

diff = output.stdout.decode("utf8")
# print(diff)
print("\n".join(generate_suggestions(diff)))
