#!/bin/bash
set -e # Exit with nonzero exit code if anything fails

TARGET_BRANCH="gh-pages"

# Pull requests and commits to other branches shouldn't try to deploy, just build to verify
if [ "$TRAVIS_PULL_REQUEST" != "false" ] || \
   [ "$TRAVIS_BRANCH" != master -a \
     "$TRAVIS_BRANCH" != develop  -a \
     "$TRAVIS_BRANCH" != doc ]; then
    echo "No docs to upload."
    exit 0
fi

key=$encrypted_2722dee00096_key
iv=$encrypted_2722dee00096_iv

mkdir -p ~/.ssh
openssl aes-256-cbc -K $key -iv $iv -in .ci/id_rsa.enc -out ~/.ssh/id_rsa -d
chmod 600 ~/.ssh/id_rsa

git clone --branch gh-pages git@github.com:stefanseefeld/faber gh_pages
cd gh_pages
git config user.name "Travis CI"
git config user.email "travis-ci"
rm -rf doc/html
mv ../build/html doc/html
git add -A doc/html
git commit -qm "Deploy to GitHub Pages: $TRAVIS_REPO_SLUG"
git push -q origin gh-pages
