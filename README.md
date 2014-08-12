github-to-assembla
==================

Script to import github issues and their comments into assembla, preserving author, tags and priority (through labels)


Setup
===================

Configure you environment variables as follows:-

* GITHUB_USER - the gituhub user account which has access to the GITHUB_AUTHOR & GITHUB_REPO repository
* GITHUB_PASS - password for above

N.B. If you wish to preserve the Original creator of tickets (issues) and comments, then your assembla user *must* have the "All" permission for the space you choose to import to.

* ASSEMBLA_KEY  - your assembla key
* ASSEMBLA_SECRET - your assembla secret
* ASSEMBLA_SPACE - the assembla space to import to
* GITHUB_AUTHOR , GITHUB_REPO  - the repo you want to import from

Now run the *print_users.py*
Use it's output to build your usermap Dictionary in the *migrate_issues.py* script.

Once you've set this up, you can run the *migrate_issues.py* and import all your issues, and tag them with the repo name they came from. Useful if migrating issues from multiple repos to one assembla space.



