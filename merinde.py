#!/usr/bin/env python3

'''
Python CMS compiling from Markdown to static HTML
'''
import markdown
import glob

from config import config

def htmlFromFile(filename):
    '''Reads file and converts markdown to HTML'''
    file_handle = open(filename)
    return markdown.markdown(file_handle.read(),output_format = config["output_format"])


# Things that should happen in here:

# 1. Get list of files that have changed / been created
compile_agenda = []
for filename in glob.glob("posts/*.md"):
    # read last changed time and compare to some time saved somewhere else (?)
    # if changed (or new), add to compile_agenda
    pass
# 2. Read them in and compile to HTML. Insert into template and do replacements.
for filename in compile_agenda:
    html = htmlFromFile(file)
    # now apply template things: use loaded template and insert contents from generated html
    # then write to file

# 3. Recompile index files. Get order by creation time of md files
if compile_agenda: #list isn't empty, so something has changed
    # get all posts, in order
    # remove index file(s)
    # load index template, fill with contents
    pass
