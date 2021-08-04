from flask import Flask

app = Flask(__name__)


@app.route('/')
def main():
    return ('<img src="https://github.com/turokg/yappa/raw/master/logo.png"/>'
            '<center><h1>Hello from Yappa! </h1>'
            "It's root url"
            '<div><a href="/json">Go to json API path</a></div></center>'
            )


@app.route('/json')
def json():
    return {
        "hello": "from Yappa!",
        "path": "json",
    }
