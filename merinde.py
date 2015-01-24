#!/usr/bin/env python3

'''
Python CMS compiling from Markdown to static HTML
'''
import markdown
import glob
import sys
import os
import re
import time

from config import config

post_template = "templates/" + config["template"] + "/post.html"
index_template = "templates/" + config["template"] + "/index.html"

mtime_regex = re.compile("<meta name=\"mtime\" content=\"(\d+)\">")
ctime_regex = re.compile("<meta name=\"ctime\" content=\"(\d+)\">")

def htmlFromFile(filename):
    '''Reads file and converts markdown to HTML'''
    file_handle = open(filename)
    return markdown.markdown(file_handle.read()) #, output_format = config["output_format"])

def getCtime(filename):
    filename = filename.replace(".md", ".html")
    file_con = open(filename).read()
    timestamps = ctime_regex.findall(file_con)
    if len(timestamps) == 1:
        return int(timestamps[0])
    else:
        raise RuntimeError("fir-ar, unexpected number of ctime tags in input file")
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
    if os.path.isfile(filename[:-3] + ".html"):
        old_html = open(filename[:-3] + ".html").read()
        matches = ctime_regex.findall(old_html)
        if len(matches) != 1:
            raise RuntimeError("Unexpected number of ctimes")
        ctime = int(matches[0])
    else:
        ctime = int(time.time())
    html = htmlFromFile(filename)
    # now apply template things: use loaded template and insert contents from generated html
    post_html = post_html_template
    post_html = post_html.replace("%content",html)
    post_html = post_html.replace("%site_name",config["site_name"])
    post_html = post_html.replace("%title",filename[:-3])
    post_html = post_html.replace("%mtime",str(int(time.time())))
    post_html = post_html.replace("%ctime",str(ctime))
    # then write to file
    open(filename[:-3] + ".html","w").write(post_html) #TODO tidy up

# 3. Recompile index files. Get order by creation time of md files
# get all posts, in order
posts = list(glob.glob("posts/*.md"))
posts_and_ctimes = sorted([(post,getCtime(post)) for post in posts], key = lambda x: x[1], reverse=True)

# remove index file(s)

# load index template, fill with contents
