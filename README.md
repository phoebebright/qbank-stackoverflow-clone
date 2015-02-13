# questionbank-stackoverflow-clone-in-django
Using questionbank as a starting point, this repo is a massive rewrite and extension to suit my needs.  Currently in progress so this code doesn't work!

The Plan:

Step 1

1. move the logic to models.py as far as possible so views become very simple - in progress
2. Build complete tests for models.py - in progress
3. Remove tags, badges, comments and versions and replace with other apps (taggit, badger...) - in progress
4. Make minimal changes to views and templates to get it working

Step 2

1. Make views class based
2. Write tests for views
3. All allauth for authentication

Step 3

1. Add API
2. Rewrite templates using Bootstrap and using API for data loading via ajax where appropriate.
