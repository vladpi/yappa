from flask import Flask

app = Flask(__name__)


@app.route('/')
def main():
    return 'root url'


@app.route('/json')
def json():
    return {
            "result": "json",
            "sub_result": {"sub": "json"}
            }
