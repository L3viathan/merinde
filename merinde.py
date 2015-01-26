#!/usr/bin/env python3

'''
Python CMS compiling from Markdown to static HTML

Usage:
    merinde.py [-f]

Options:
    -f      forces recompile
'''
import json
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

index_regex = re.compile("%begin(.*)%end", re.MULTILINE + re.DOTALL)

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

def makeStars(stardict):
    s = "<table class='rating-table'>\n"
    for attribute in stardict:
        s += "<tr><td class='rating-label'>" + attribute + "</td><td class='rating-stars'><span class='rating-stars-full'>" + ("★" * stardict[attribute]) + "</span><span class='rating-stars-empty'>" + ("☆" * (config["max_stars"] - stardict[attribute])) + "</span></span></td></tr>\n"
    s += "</table>"
    return s

def makeSqimg(matchObject):
    return "<img class='sqimg' src='../images/" + matchObject.group(1) + "' /><br>"

def makeMap(matchObject):
    return "<img class='map' src='https://maps.googleapis.com/maps/api/staticmap?center=" + matchObject.group(1) + "&zoom=15&size=300x150&markers=color:green|" + matchObject.group(1) + "' /><br>"

def makeLoc(matchObject):
    return "<div class='location-label'>" + matchObject.group(1) + "</div>"

def makeWebsite(matchObject):
    return "<a class='external-link' href='" + matchObject.group(1) + "'>Website</a>"

# Things that should happen in here:

# 1. Get list of files that have changed / been created
compile_agenda = []
for filename in glob.glob("posts/*.json"):
    # read last changed time and compare to some time saved somewhere else (?)
    # if changed (or new), add to compile_agenda
    if args["-f"] or not os.path.isfile(filename[:-5] + ".html"): #we have never compiled it
        compile_agenda.append(filename)
        continue
    mtime = os.path.getmtime(filename)
    print("trying to open",filename)
    data = json.load(open(filename))
    if data.get('mtime',0) < mtime: #not found or modified
        compile_agenda.append(filename)


if not compile_agenda: #empty agenda, nothing to do
    print("Nothing to do, exiting")
    sys.exit(0)

post_html_template = open(post_template).read()

# 2. Read them in and compile to HTML. Insert into template and do replacements.
for filename in compile_agenda:
    data = json.load(open(filename))
    data['ctime'] = data.get('ctime',int(time.time()))
    data['mtime'] = int(time.time())
    json.dump(data,open(filename,"w"), indent=4)
    # now apply template things: use loaded template and insert contents from generated html
    post_html = post_html_template
    post_html = post_html.replace("%description",data["description"])
    post_html = post_html.replace("%site_name",config["site_name"])
    post_html = post_html.replace("%title",data["title"])

    # more complicated replacements:
    post_html = post_html.replace("%stars",makeStars(data["stars"]))
    post_html = post_html.replace("%image",data["image"])
    post_html = post_html.replace("%latlon",data["location"]["latlon"])
    post_html = post_html.replace("%loc",data["location"]["name"])
    post_html = post_html.replace("%website",data.get("website", ""))
    # then write to file
    open(filename[:-5] + ".html","w").write(post_html) #TODO tidy up

# 3. Recompile index files. Get order by creation time of md files
# get all posts, in order
posts = list(glob.glob("posts/*.json"))
posts_and_ctimes = sorted([(post,json.load(open(post))["ctime"]) for post in posts], key = lambda x: x[1], reverse=True)
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
        data = json.load(open(post))
        loop_html = loop_html_template
        loop_html = loop_html.replace("%link",post[:-5] + ".html")
        loop_html = loop_html.replace("%description", data["description"])
        loop_html = loop_html.replace("%title", data["title"])
        loop_html = loop_html.replace("%loc", data["location"]["name"])
        inner_html += loop_html
    html = index_regex.sub(inner_html, html)
    print("Index",index)
    i = "" if index == 0 else "-" + str(index)
    with open("index"+i+".html", "w") as fw:
        fw.write(html)

