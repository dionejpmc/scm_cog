#!/bin/bash -e
CURRENTDATE=$(date)
git config --global user.email "dionejpmc@gmail.com"
git config --global user.name "dionejpmc"
git add *
git commit -m "Commit $CURRENTDATE"
git push -u origin dev 
#https://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@github.com/dionejpmc/scm_cog.git


