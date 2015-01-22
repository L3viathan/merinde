#!/usr/bin/env python3

'''
Python CMS compiling from Markdown to static HTML
'''
import markdown
from config import config

def htmlFromFile(filename):
    '''Reads file and converts markdown to HTML'''
    file_handle = open(filename)
    return markdown.markdown(file_handle.read(),output_format = config["output_format"])


# Things that should happen in here:

# 1. Get list of files that have changed / been created
# 2. Read them in and compile to HTML. Insert into template and do replacements.
# 3. Recompile index files. Get order by creation time of md files
