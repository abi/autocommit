# aicommit - AI-generated Git commit messages

A simple CLI tool that generates 5 commit message suggestions for the changes in your current Git repo. After you pick and edit the commit message you want, it commits the changes.

![CleanShot 2023-01-05 at 15 55 47](https://user-images.githubusercontent.com/23818/211055859-7fa8b320-e2d6-41c4-ac29-7f441364666d.gif)

### Installation

**`pip install aicommit`**

On first run, it will prompt you for your OpenAI API key. Sign up for OpenAI if you haven't. Grab your API key by going to the dropdown on the top right, selecting "View API Keys" and creating a new key. Copy this key.

**NOTE:** it commits all changes, untracked and unstaged, in your current repo.

# Feedback/thoughts

Ping me on [Twitter](https://twitter.com/_abi_)

## scan_repo

`scan_repo` runs through all the commits in your repository to generate a CSV with AI-suggested commit messages side-by-side with your original commit messages. [Read more about this tool here](https://abiraja.substack.com/p/ai-generated-git-commit-messages)

To run scan_repo, copy `.env.example` to `.env` and add your OPENAI_KEY.

To update the repo it runs on, modify the `GITHUB_REPO_URL` variable at the top of `scan_repo.py`


# Publishing to pip

Version bump and clear out `dist/`

```
python3 -m build
twine check dist/*
twine upload dist/* --verbose
```
