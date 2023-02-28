#!/bin/bash

set -xeu -o pipefail

git config user.name "github-actions[bot]"
git config user.email "github-actions[bot]@users.noreply.github.com"
commit_message="BGforgeNet/handle-charsets"

args="--tra-path $INPUT_TRA_PATH --out-path $INPUT_OUT_PATH"

if [[ "$INPUT_FROM_UTF8" == "true" ]]; then
    args="$args --from-utf8"
fi

if [[ "$INPUT_SPLIT_CONSOLE" == "true" ]]; then
    args="$args --split-console"
fi

# we specifically want word splitting
# shellcheck disable=SC2086
./handle.py $args

# now commit and push
if [[ "$INPUT_COMMIT" != "true" ]]; then
    exit 0
fi
if [[ "$(git status --porcelain "$INPUT_OUT_PATH" | wc -l)" == "0" ]]; then
    echo "no changes found"
else
    echo "Changes found"
    git add "$INPUT_OUT_PATH"
    git commit -m "$commit_message"
    echo "Pushing changes"
    git push
fi
