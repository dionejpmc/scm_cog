echo "# scm_cog" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M dev
git remote add origin https://github.com/dionejpmc/scm_cog.git
git push -u origin dev