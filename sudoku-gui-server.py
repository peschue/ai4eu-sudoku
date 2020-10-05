from typing import Optional, List
import os
import logging
import json
import time
import fastapi
import fastapi.templating
import pydantic

logger = logging.getLogger(__name__)
#logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.DEBUG)


class FieldSpec(pydantic.BaseModel):

    x: int
    y: int
    content: Optional[int]
    cssclass: Optional[str]

class GUIUpdate(pydantic.BaseModel):

    statusbar: str
    field: List[FieldSpec]


def create_app() -> fastapi.FastAPI:

    app = fastapi.FastAPI(title='SudokuGUIServer', debug=True)
    app.logger = logger
    return app

app = create_app()

configfile = os.environ['CONFIG'] if 'CONFIG' in os.environ else "sudoku-gui-server-config.json"
logging.info("loading config from %s", configfile)
config = json.load(open(configfile, 'rt'))

templates = fastapi.templating.Jinja2Templates(directory='templates')

@app.get('/')
def serve_website(request: fastapi.Request):
    return templates.TemplateResponse("sudoku-gui.html", { 'request': request })

@app.get('/sudoku-gui.js')
def serve_js(request: fastapi.Request):
    return fastapi.responses.FileResponse("sudoku-gui.js")

@app.get('/sudoku-gui.css')
def serve_css(request: fastapi.Request):
    return fastapi.responses.FileResponse("sudoku-gui.css")

@app.put('/user_setcell', response_model=None)
def setcell(x: int, y: int, value: Optional[int] = None) -> None:
    '''
    If the user changes a cell value in the GUI,
    this PUT request is sent.
    '''
    logging.info("user_setcell(%d,%d,%s)", x, y, value)

    logging.warning("TODO IMPLEMENT")

    return None

@app.get('/wait_update', response_model=Optional[GUIUpdate])
def wait_update(timeout_ms: int):
    '''
    The GUI periodically calls this method to wait for a new
    update to the GUI. Ideally the GUI calls this each <timeout_ms>
    milliseconds.
    '''
    logging.info("wait_update(%d)", timeout_ms)
    ret = None

    time.sleep(5)
    logging.warning("TODO IMPLEMENT")

    ret = GUIUpdate(statusbar="new status", field=[])
    ret.field.append(FieldSpec(x=1,y=1,content=27,cssclass='invalid'))

    logging.info("wait_update returns (%s)", ret)
    return ret
