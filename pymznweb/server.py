from aiohttp import web
from typing import Dict, Optional
import json
import asyncio
import time

NUM_CONCURRENT_JOBS = 10
TIMEOUT_MS = 30000

sem = asyncio.Semaphore(NUM_CONCURRENT_JOBS)

def create_data_args(kv: Optional[Dict[str,str]]):
    if kv is not None:
        return [f"-D {key}={value}" for key, value in kv.items()]
    else:
        return []

MZ_SOLN_SEP = '----------'
MZ_UNSAT_MSG = '=====UNSATISFIABLE====='
MZ_UNSAT_OR_UNBOUNDED_MSG = '=====UNSATorUNBOUNDED====='
MZ_UNBOUNDED_MSG = '=====UNBOUNDED====='
MZ_UNKNOWN_MSG = '=====UNKNOWN====='
MZ_ERROR_MSG = '=====ERROR====='
MZ_COMPLETE_MSG = '=========='

STATUS_UNSAT = 'unsat'
STATUS_UNSAT_OR_UNBOUNDED = 'unsatOrUnbounded'
STATUS_UNBOUNDED = 'unbounded'
STATUS_UNKNOWN = 'unknown'
STATUS_ERROR = 'error'
STATUS_COMPLETE = 'complete'

def interpret_minizinc_json_output(stdout: str):
    if MZ_SOLN_SEP in stdout:
        output, message = stdout.rsplit(MZ_SOLN_SEP, 1)
    else:
        # if there is no solution at all, there is no MZ_SOLN_SEP
        # and therefore only look for message
        output = None
        message = stdout

    message = message.strip()

    if message == MZ_UNSAT_MSG:
        return STATUS_UNSAT, None
    elif message == MZ_UNSAT_OR_UNBOUNDED_MSG:
        return STATUS_UNSAT_OR_UNBOUNDED, None
    elif message == MZ_UNBOUNDED_MSG:
        return STATUS_UNBOUNDED, None
    elif message == MZ_UNKNOWN_MSG:
        return STATUS_UNKNOWN, None
    elif message == MZ_ERROR_MSG:
        return STATUS_ERROR, None
    elif message == MZ_COMPLETE_MSG:
        return STATUS_COMPLETE, json.loads(output)
    else:
        raise ValueError(f"unknown minizinc status message '{message}' to output '{output}'")

async def echo(request: web.Request):
    return web.Response(text='MiniZinc')

async def handle_raw(request: web.Request):
    try:
        start_queue_time = time.time()
        await sem.acquire()
        stop_queue_time = start_compute_time = time.time()

        # get json body
        req = await request.json()

        stdin: bytes = req['stdin'].encode()
        args = req['args']

        # call minizinc
        args = ["minizinc"] + args + ["-"]

        proc = await asyncio.create_subprocess_exec(
            *args,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)

        # read output
        stdout, stderr = await proc.communicate(stdin)
        
        stop_compute_time = time.time()

        # send back
        res = {
            'stdout': stdout.decode(),
            'stderr': stderr.decode(),
            'returncode': proc.returncode,
            'queueTimeMs': int((stop_queue_time - start_queue_time)*1000),
            'computeTimeMs': int((stop_compute_time - start_compute_time)*1000)
        }

        return web.Response(text=json.dumps(res), content_type='application/json')
    finally:
        sem.release()

async def handle_json(request: web.Request):
    try:
        start_queue_time = time.time()
        await sem.acquire()
        stop_queue_time = start_compute_time = time.time()

        # get json body
        req = await request.json()

        problem: str = req['problem']
        data_args = create_data_args(req.get('data'))
        
        if 'args' in req:
            extra_args = req['args']
        else:
            extra_args = []

        if 'timeoutMs' in req and isinstance(req['timeoutMs'], int) and req['timeoutMs'] > 0:
            timeout_ms = req['timeoutMs']
        else:
            timeout_ms = TIMEOUT_MS

        # call minizinc
        args = ["minizinc", "--time-limit", str(timeout_ms), "--output-mode", "json"] + data_args + extra_args + ["-"]

        proc = await asyncio.create_subprocess_exec(
            *args,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)

        # read output
        stdout, stderr = await proc.communicate(problem.encode())
        
        stop_compute_time = time.time()

        if proc.returncode == 0:
            status, result = interpret_minizinc_json_output(stdout.decode())
        else:
            status = STATUS_ERROR
            result = None

        # send back
        res = {
            'result': status,
            'values': result,
            'stdout': stdout.decode(),
            'stderr': stderr.decode(),
            'returncode': proc.returncode,
            'queueTimeMs': int((stop_queue_time - start_queue_time)*1000),
            'computeTimeMs': int((stop_compute_time - start_compute_time)*1000)
        }

        return web.Response(text=json.dumps(res), content_type='application/json')
    finally:
        sem.release()

def create_app(argv=None):
    app = web.Application()
    app.router.add_get('/', echo)
    app.router.add_post('/raw', handle_raw)
    app.router.add_post('/json', handle_json)
    return app

# run it with: `python3 -m aiohttp.web pymznweb.server:create_app`
