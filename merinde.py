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
