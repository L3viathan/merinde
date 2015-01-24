#!/usr/bin/env python3

'''
Python CMS compiling from Markdown to static HTML

Usage:
    merinde.py [-f]

Options:
    -f      forces recompile
'''
import markdown
import glob
import sys
import os
import re
import time
import math

from docopt import docopt
from config import config

args = docopt(__doc__,version="0.1")

post_template = "templates/" + config["template"] + "/post.html"
index_template = "templates/" + config["template"] + "/index.html"

mtime_regex = re.compile("<meta name=\"mtime\" content=\"(\d+)\">")
ctime_regex = re.compile("<meta name=\"ctime\" content=\"(\d+)\">")
index_regex = re.compile("%begin(.*)%end", re.MULTILINE + re.DOTALL)
title_regex = re.compile("^# ?(.*)$", re.MULTILINE)
star_regex = re.compile("%stars (\w+) (\d)$", re.MULTILINE)
sqimg_regex = re.compile("%sqimg (.*)$", re.MULTILINE)

def htmlFromFile(filename):
    '''Reads file and converts markdown to HTML'''
    file_handle = open(filename)
    md = file_handle.read()
    return (markdown.markdown(md),md) #, output_format = config["output_format"])

def getCtime(filename):
    filename = filename.replace(".md", ".html")
    file_con = open(filename).read()
    timestamps = ctime_regex.findall(file_con)
    if len(timestamps) == 1:
        return int(timestamps[0])
    else:
        raise RuntimeError("fir-ar, unexpected number of ctime tags in input file")

def chunks(l, n):
    """ Yield successive n-sized chunks from l.
        adapted from: http://stackoverflow.com/a/312464/1016216
    """
    if n == 0:
        n = 99999
    for i in range(0, len(l), n):
        yield l[i:i+n]

def makePrevNext(index,num):
    s = ""
    if index != 0:
        s += "<a class='previous-page' href='" + "index" + ("" if index == 1 else "-"+str(index-1)) + ".html'>Previous</a>"
    if index != num-1:
        s += "<a class='next-page' href='" + "index" + "-"+str(index+1) + ".html'>Next</a>"
    return s

def getTitle(md):
    matches = title_regex.findall(md)
    if matches:
        return matches[0]
    else:
        return "No title"

def makeStars(matchObject):
    num = int(matchObject.group(2))
    return "<div class='rating'><span class='rating-label'>" + matchObject.group(1) + "</span><span class='rating-stars'><span class='rating-stars-full'>" + ("★" * num)  + "</span><span class='rating-stars-empty'>"+ ("☆" * (7-num)) + "</span></span></div>"

def makeSqimg(matchObject):
    return "<img class='sqimg' src='../images/" + matchObject.group(1) + "' /><br>"

# Things that should happen in here:

# 1. Get list of files that have changed / been created
compile_agenda = []
for filename in glob.glob("posts/*.md"):
    # read last changed time and compare to some time saved somewhere else (?)
    # if changed (or new), add to compile_agenda
    if args["-f"] or not os.path.isfile(filename[:-3] + ".html"): #we have never compiled it
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
    (html, md) = htmlFromFile(filename)
    # now apply template things: use loaded template and insert contents from generated html
    post_html = post_html_template
    post_html = post_html.replace("%content",html)
    post_html = post_html.replace("%site_name",config["site_name"])
    post_html = post_html.replace("%title",getTitle(md))
    post_html = post_html.replace("%mtime",str(int(time.time())))
    post_html = post_html.replace("%ctime",str(ctime))

    # more complicated replacements:
    post_html = star_regex.sub(makeStars,post_html)
    post_html = sqimg_regex.sub(makeSqimg,post_html)
    # then write to file
    open(filename[:-3] + ".html","w").write(post_html) #TODO tidy up

# 3. Recompile index files. Get order by creation time of md files
# get all posts, in order
posts = list(glob.glob("posts/*.md"))
posts_and_ctimes = sorted([(post,getCtime(post)) for post in posts], key = lambda x: x[1], reverse=True)
print(posts_and_ctimes)
# remove index file(s)
for f in glob.glob("index*.html"):
    os.remove(f)
# load index template, fill with contents
index_html_template = open(index_template).read()

number_of_pages = int(math.ceil(len(posts_and_ctimes)/config["pagination"]))

for (index,chunk) in enumerate(chunks(posts_and_ctimes,config["pagination"])):
    html = index_html_template
    html = html.replace("%site_name", config["site_name"])
    html = html.replace("%prevnext", makePrevNext(index,number_of_pages))
    loop_html_template = index_regex.findall(html)[0] # todo: make safe
    inner_html = ""
    for (post,c) in chunk:
        (content,md) = htmlFromFile(post)
        loop_html = loop_html_template
        loop_html = loop_html.replace("%link",post[:-3] + ".html")
        loop_html = loop_html.replace("%content", content)
        loop_html = loop_html.replace("%title", getTitle(md))
        inner_html += loop_html
    html = index_regex.sub(inner_html, html)
    print("Index",index)
    i = "" if index == 0 else "-" + str(index)
    with open("index"+i+".html", "w") as fw:
        fw.write(html)

