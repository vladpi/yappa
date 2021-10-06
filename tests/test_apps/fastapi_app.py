from fastapi import FastAPI
from pydantic import BaseModel

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


class Request(BaseModel):
    test_str: str
    test_num: int


@app.post('/post')
def post(request: Request):
    return {"request": request}
