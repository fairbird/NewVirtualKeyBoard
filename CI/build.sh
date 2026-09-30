#!/bin/sh

# Script by Persian Prince for https://github.com/OpenVisionE2
# You're not allowed to remove my copyright or reuse this script without putting this header.

# NewVirtualKeyBoard: runs on the branch the workflow was started for
# (buildbot.yml: pushes to main) and pushes the cleanup commits back to it.
BRANCH="${GITHUB_REF_NAME:-main}"

setup_git() {
  git config --global user.email "41898282+github-actions[bot]@users.noreply.github.com"
  git config --global user.name "github-actions[bot]"
}

commit_files() {
  git clean -fd
  rm -rf *.pyc
  rm -rf *.pyo
  rm -rf *.mo
  git checkout "$BRANCH"
  ./CI/chmod.sh
  ./CI/dos2unix.sh
  ./CI/PEP8.sh
}

upload_files() {
  # origin carries the workflow's token (actions/checkout, contents: write)
  git push --quiet origin "$BRANCH" || echo "failed to push with error $?"
}

setup_git
commit_files
upload_files
