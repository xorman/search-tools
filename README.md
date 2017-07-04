search-tools
==========================
This is a repo for tools that search files on the local file system.

search.py
---------------
Offline search for files and file content using a short command. This script
generates and invokes a tailored `find` and `grep` command with a selection of
switches activated by default. Some switches increase the search speed but might
also exclude relevant findings. For instance, option -g by default only
searches patterns in files with -size -2000k

- Please refer to the command line help (-h)
- Use `pydoc ./search.py` for developer documentation
- Or read the source :)
 
