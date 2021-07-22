from flask import Flask, request

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


@app.route("/query_params")
def query_params():
    return {"params": request.args}


@app.route("/url_param/<param>")
def url_param(param):
    return {"param": param}


@app.route("/post/", methods=["POST"])
def post():
    return {"request": request.get_json(force=True)}
