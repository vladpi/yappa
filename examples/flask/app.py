from flask import Flask
from jinja2 import FileSystemLoader, Environment

app = Flask(__name__)

env = Environment(loader=FileSystemLoader("templates"))


@app.route('/')
def main():
    return ('<center>'
            '<img src="https://github.com/turokg/yappa/raw/master/logo.png"/>'
            '<h1>Hello from Yappa! </h1>'
            "It's root url"
            '<div><a href="/json">Go to json API</a></div>'
            '<div><a href="/jinja">Go to Jinja2 rendered html</a></div>'
            '</center>'
            )


@app.route('/json')
def json():
    return {
        "hello": "from Yappa!",
        "path": "json",
    }

@app.route('/jinja')
def jinja():
    template = env.get_template("sample.html")
    return template.render({"message": "Hello world! -- from jinja"})

