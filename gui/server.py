from typing import Optional, List
import os
import logging
import json
import time
import fastapi
import fastapi.templating
import pydantic
import queue
import grpc
import concurrent.futures
import sys

sys.path.append('../protobuf/')
import sudoku_gui_pb2_grpc
import sudoku_gui_pb2

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

class GRPCResultProcessor(sudoku_gui_pb2_grpc.SudokuDesignEvaluationResultProcessorServicer):
    def __init__(self, to_js_queue):
        self.to_js_queue = to_js_queue

    def processEvaluationResult(self, request, context):
        logging.info("received evaluation result")

        # pass this to javascript to send it to the GUI
        statusstr = {
            0: 'Sudoku has no solution',
            1: 'Sudoku has a unique solution',
            2: 'Sudoku has multiple solutions'
        }[request.status]
        fields = []
        if request.status == 1:
            for v, xy in zip(request.solution, [ (col,row) for row in range(1,10)  for col in range(1,10)]):
                #logging.info("v %d xy %s", v, xy)
                fields.append(FieldSpec(x=xy[0], y=xy[1], content=v, cssclass='solution'))

        gu = GUIUpdate(statusbar=statusstr, field=fields)
        self.to_js_queue.put(gu)

        # dummy return
        return sudoku_gui_pb2.Empty(empty=0)


def create_app() -> fastapi.FastAPI:

    app = fastapi.FastAPI(title='SudokuGUIServer', debug=True)
    app.logger = logger
    return app

app = create_app()

configfile = os.environ['CONFIG'] if 'CONFIG' in os.environ else "../config.json"
logging.info("loading config from %s", configfile)
config = json.load(open(configfile, 'rt'))
protobuf_to_js_queue = queue.Queue()
js_to_protobuf_queue = queue.Queue()
templates = fastapi.templating.Jinja2Templates(directory='templates')

grpcserver = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=10))
sudoku_gui_pb2_grpc.add_SudokuDesignEvaluationResultProcessorServicer_to_server(GRPCResultProcessor(protobuf_to_js_queue), grpcserver)
grpcport = config['gui-grpcport']
grpcserver.add_insecure_port('localhost:'+str(grpcport))
logging.info("starting grpc server at port %d", grpcport)
grpcserver.start()

@app.get('/')
def serve_website(request: fastapi.Request):
    return templates.TemplateResponse("gui.html", { 'request': request })

@app.get('/gui.js')
def serve_js(request: fastapi.Request):
    return fastapi.responses.FileResponse("gui.js")

@app.get('/gui.css')
def serve_css(request: fastapi.Request):
    return fastapi.responses.FileResponse("gui.css")

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

    try:
        ret = protobuf_to_js_queue.get(block=True, timeout=timeout_ms/1000.0)
    except queue.Empty:
        pass

    logging.info("wait_update returns (%s)", ret)
    return ret
