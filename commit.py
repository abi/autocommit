import subprocess
import pygit2

from llm import generate_suggestions

repo = pygit2.Repository(".")

git_command = "git --no-pager diff; for next in $( git ls-files --others --exclude-standard ) ; do git --no-pager diff --no-index /dev/null $next; done;"
output = subprocess.run(git_command, shell=True,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)

diff = output.stdout.decode("utf8")

print("\n".join(generate_suggestions(diff)))

# print(diff)

# Handle errors here

# print(output.stderr)
# print(output.returncode)
