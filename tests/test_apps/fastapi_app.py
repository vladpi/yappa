from fastapi import FastAPI

app = FastAPI()


@app.get('/')
def main():
    return 'root url'


@app.get('/json')
def json():
    return {
            "result": "json",
            "sub_result": {"sub": "json"}
            }
