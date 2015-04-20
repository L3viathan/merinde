# merinde
Python CMS compiling from JSON to static HTML

## Setup
To install the required Python modules, run `pip3 install -r requirements.txt` after checking out the repository.

## Usage
Once installed, use `python3 merinde.py` to generate the HTML, and `python3 -f merinde.py` to force regeneration of everything (important if you changed no files, but made a template or config adjustment.

## Configuration
Edit config.py to change settings. Currently there are 5 settings available, none of them are optional:

- output: Defaults to "html5", other possibility: "xhtml"
- template: The template that is used to generate the html
- site_name: The title of the website. Used by the default template for the title.
- pagination: After how many posts to split the index pages
- max_stars: You can change that to e.g. 3 to have a 3-star rating system

## Templates
The template language is pretty simple right now, which is why I won't add full documentation at this point. If you want your own template, the best option is to copy the `default` folder in `templates/` and change things in there, since every feature of the template language is used in there. In short, you'll need a `index.html` and a `post.html`. You may also add any number of additional files (e.g. css) that you can refer to from those two files.

### post.html
An individual post uses this template. Percentage signs (`%`) are used to denote "variables" that will get replaced by merinde. For a list of options, look at the default template.

### index.html
This is the template your index files will be generated from. Generally, you can only use the `%site_name` and the special `%prev_next` variables in here. However, you can (and should) define a block encased by `%begin` and `%end`, which will be repeated for every post in this index file. In there, you can use all post-specific variables.
