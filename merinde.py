#!/usr/bin/env python3

'''
Python CMS compiling from Markdown to static HTML
'''
import markdown
import glob
import sys
import os
import re

from config import config

post_template = "templates/" + config["template"] + "/post.html"
index_template = "templates/" + config["template"] + "/index.html"

mtime_regex = re.compile("<meta name=\"mtime\" content=\"(\d+)\">")
ctime_regex = re.compile("<meta name=\"ctime\" content=\"(\d+)\">")

def htmlFromFile(filename):
    '''Reads file and converts markdown to HTML'''
    file_handle = open(filename)
    return markdown.markdown(file_handle.read()) #, output_format = config["output_format"])


# Things that should happen in here:

# 1. Get list of files that have changed / been created
compile_agenda = []
for filename in glob.glob("posts/*.md"):
    # read last changed time and compare to some time saved somewhere else (?)
    # if changed (or new), add to compile_agenda
    if not os.path.isfile(filename[:-3] + ".html"): #we have never compiled it
        compile_agenda.append(filename)
        continue
    mtime = os.path.getmtime(filename)
    html = open(filename[:-3] + ".html").read()
    matches = mtime_regex.findall(html)
    if len(matches) != 1 or int(matches[0]) < mtime: #not found or modified
        compile_agenda.append(filename)


if not compile_agenda: #empty agenda, nothing to do
    print("Nothing to do, exiting")
    sys.exit(0)

post_html_template = open(post_template).read()

# 2. Read them in and compile to HTML. Insert into template and do replacements.
for filename in compile_agenda:
    html = htmlFromFile(filename)
    # now apply template things: use loaded template and insert contents from generated html
    post_html = post_html_template
    post_html = post_html.replace("%content",html)
    post_html = post_html.replace("%site_name",config["site_name"])
    post_html = post_html.replace("%title",filename[:-3])
    # then write to file
    open(filename[:-3] + ".html","w").write(post_html) #TODO tidy up

# 3. Recompile index files. Get order by creation time of md files
# get all posts, in order
# remove index file(s)
# load index template, fill with contents
