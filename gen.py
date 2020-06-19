#!/usr/bin/env python3

from glob import glob
from jinja2 import Template
from markdown import Markdown

class Post:
    def __init__(self, content, filename, title, date, post_type):
        self.content = content
        self.filename = filename[:-2]
        self.title = title
        self.date = date
        self.post_type = post_type

    def render_html(self):
        if self.post_type == "content":
            with open("templates/content.html", "r") as file:
                template = Template(file.read())
                self.html = template.render(content=self.content, title=self.title, date=self.date)

        elif self.post_type == "meta":
            with open("templates/meta.html", "r") as file:
                template = Template(file.read())
                self.html = template.render(content=self.content, title=self.title)

    def write_to_file(self):
        with open(self.filename + "html", "w") as file:
            file.write(self.html)

def get_posts(post_path, post_type):
    post_list = []

    for post in glob(post_path):
        if post == "README.md":
            pass

        else:
            with open(post, "r") as file:
                data = file.read()
                md = Markdown(extensions=["meta", "fenced_code"])
                content = md.convert(data)
                title = md.Meta["title"].pop()

                try:
                    date = md.Meta["date"].pop()
                except KeyError:
                    date = None

                post_list.append(Post(content, file.name, title, date, post_type))

    return post_list

def make_html(post_list):
    for post in post_list:
        post.render_html()
        post.write_to_file()

content_posts = get_posts("./content/*.md", "content")
content_posts.sort(key=lambda post: post.date, reverse=True)

with open("index.md", "w") as file:
    file.write("title: Index\n\n")

    for post in content_posts:
        file.write("[{}]({}) ({})\n\n".format(post.title, post.filename + "html", post.date))

meta_posts = get_posts("*.md", "meta")

make_html(content_posts)
make_html(meta_posts)
