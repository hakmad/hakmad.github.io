#!/usr/bin/env python3

import markdown

from glob import glob
from jinja2 import Template

class Post:
    def __init__(self, title, date, content, filename):
        self.title = title
        self.date = date
        self.content = content
        self.filename = filename

    def render_html(self):
        with open("templates/post.html", "r") as file:
            template = Template(file.read())

        self.html = template.render(content = self.content, title = self.title, date = self.date)

        with open(self.filename[:-2] + "html", "w") as file:
            file.write(self.html)

posts = []

for post in glob("./content/*.md"):
    with open(post, "r") as file:
        data = file.read()

        md = markdown.Markdown(extensions = ["meta", "fenced_code"])

        content = md.convert(data)
        title = md.Meta["title"][0]
        date = md.Meta["date"][0]
        filename = file.name

        posts.append(Post(title, date, content, filename))

posts.sort(key = lambda x: x.date, reverse = True)

with open("index.md", "w") as file:
    file.write("# Index\n\n")

for post in posts:
    post.render_html()

    title = post.title
    date = post.date
    filename = post.filename[:-2] + "html"

    with open("index.md", "a") as file:
        file.write("[{}]({}) ({})\n\n".format(title, filename, date))

for post in glob("*.md"):
    if post == "README.md":
        pass
    else:
        with open(post, "r") as file:
            data = file.read()
            filename = file.name
    
            md = markdown.Markdown()
            title = file.name[:-3].title()
            content = md.convert(data)
    
        with open("templates/meta.html", "r") as file:
            template = Template(file.read())
    
        html = template.render(content = content, title = title)
    
        with open(filename[:-2] + "html", "w") as file:
            file.write(html)
