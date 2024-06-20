from starlette.responses import Response, JSONResponse
from starlette.requests import Request
from fastapi import FastAPI
from starlette.background import BackgroundTask
import os
from .call_state import CallState, call_dict
from .conversation_controller import ConversationController
import asyncio
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()

my_xml = './dialogtree_phonebot/dialogtree/example.xml'

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.post('/make-call')
async def browser_conversation_socket(request:Request)->JSONResponse:
    # print('got to make call', flush=True)
    call_sid = (await request.json())['call_sid']
    controller = ConversationController()
    call_state = CallState(
        call_sid=call_sid,
        outbound_xml=my_xml,
        inbound_xml=my_xml,
        controller=controller
    )
    inner_task = asyncio.ensure_future(call_state.manage_call('inbound'))
    task = BackgroundTask(wait_until_end, inner_task)
    response = await call_state.get_response()
    
    return JSONResponse(response, background=task)

async def wait_until_end(task):
   await task

@app.post('/converse')
async def browser_conversation_socket(request:Request)->JSONResponse:
    r = await request.json()
    print(json.dumps(r, indent=4), flush=True)
    await call_dict[r['call_sid']].send(r['quote'])
    response = await call_dict[r['call_sid']].get_response()
    print('there you are')
    
    return JSONResponse(content=response)

import uvicorn
uvicorn.run(app, host='0.0.0.0', port=int(8080))


