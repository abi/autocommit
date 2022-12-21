# autocommit

AI-Generated Git Commit Messages

Includes two tools: `commit.py` and `scan_repo.py`

## commit

An interactive CLI tool that generates 5 commit message suggestions for all the changes in your current Git repo. After you pick and edit the commit message you want, it performs the commit.

**NOTE:** it commits all changes, untracked and unstaged, in your current repo.

On first run, it will prompt you for your OpenAI API key. Sign up for OpenAI if you haven't. Grab your API key by going to the dropdown on the top right, selecting "View API Keys" and creating a new key. Copy this key.

![CleanShot 2022-11-03 at 21 59 03](https://user-images.githubusercontent.com/23818/208987015-637ee18e-fa06-4096-8fe4-2d59ba1523d9.gif)


## scan_repo

`scan_repo` runs through all the commits in your repository to generate a CSV with AI-suggested commit messages side-by-side with your original commit messages.

To run scan_repo, copy `.env.example` to `.env` and add your OPENAI_KEY.

To update the repo it runs on, modify the `GITHUB_REPO_URL` variable at the top of `scan_repo.py`
