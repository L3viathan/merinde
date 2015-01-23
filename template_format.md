# Merinde Template Language

## General functionality
There are global variables and post-specific variables. Some (like ctime) are set automatically.
Post-specific variables are also available in the loop in an index file.

## Variables

- %content: content of a post.
- %title: page title
- %site_name: name of the site
- %ctime, %mtime: time of creation and modification

## Functions
- %begin, %end: denote the "loop" in the index file
- %star: inserts fancy star thing. Two parameters: name, amount
