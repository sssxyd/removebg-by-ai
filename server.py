from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Response

from removebg import RemoveBgDTO, process

app = FastAPI()
app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")


@app.get("/")
async def index_html():
    return FileResponse('static/index.html')


@app.get("/vite.svg")
async def index_html():
    return FileResponse('static/vite.svg')


@app.post("/removebg")
async def removebg_post(dto: RemoveBgDTO):
    code, msg, result = process(dto=dto)
    if code != 0:
        return {'code': code, 'msg': msg, 'result': ''}
    if dto.responseFormat == 0:
        return {'code': code, 'msg': msg, 'result': f"data:image/png;base64,{result}"}
    else:
        return Response(content=result, media_type="image/png")


@app.get("/removebg")
async def removebg_get(url: str):
    dto = RemoveBgDTO(url=url, responseFormat=1)
    code, msg, result = process(dto=dto)
    if code != 0:
        return {'code': code, 'msg': msg, 'result': ''}
    return Response(content=result, media_type="image/png")
