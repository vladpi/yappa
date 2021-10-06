from fastapi import FastAPI
from pydantic import BaseModel
from starlette.responses import PlainTextResponse

app = FastAPI()


@app.get('/')
def main():
    return PlainTextResponse('root url')


@app.get('/json')
def json():
    return {
        "result": "json",
        "sub_result": {"sub": "json"}
    }


@app.get("/path_param/{param}")
def path_param(param):
    return {"param": param}


class Request(BaseModel):
    test_str: str
    test_num: int


@app.post('/post')
def post(request: Request):
    return {"request": request}
