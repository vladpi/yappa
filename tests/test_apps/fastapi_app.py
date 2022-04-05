from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel
from starlette.responses import PlainTextResponse, FileResponse, Response

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


@app.get('/file')
def file():
    path = "tmp_file.zip"
    with open(path, "w+") as f:
        f.write(path)
    return FileResponse(path)


@app.get('/jpeg')
def jpeg():
    path = Path(Path(__file__).resolve().parent, "image.jpeg")
    with open(path, "rb") as f:
        content = f.read()
    return Response(content=content, media_type="image/jpeg")
