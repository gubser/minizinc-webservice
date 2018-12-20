from aiohttp import web
from typing import Dict
import json
import asyncio
import time

NUM_CONCURRENT_JOBS = 10
TIMEOUT_MS = 30000

sem = asyncio.Semaphore(NUM_CONCURRENT_JOBS)

async def handle(request: web.Request):
    try:
        start_queue_time = time.time()
        await sem.acquire()
        stop_queue_time = start_compute_time = time.time()

        # get json body
        req = await request.json()

        problem: str = req['problem']
        if 'data' in req:
            data_params = [f"-D {key}={value}" for key, value in req['data'].items()]
        else:
            data_params = []
        
        if 'args' in req:
            extra_args = req['args']
        else:
            extra_args = []

        if 'timeoutMs' in req:
            timeout_ms = req['timeoutMs']
        else:
            timeout_ms = TIMEOUT_MS

        # call minizinc
        args = ["minizinc", "--time-limit", str(timeout_ms)] + data_params + extra_args + ["-"]

        proc = await asyncio.create_subprocess_exec(
            *args,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)

        # read output
        stdout, stderr = await proc.communicate(problem.encode())
        
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

def init(argv=None):
    app = web.Application()
    app.router.add_post('/minizinc', handle)
    return app

# run it with: `python3 -m aiohttp.web pymznweb.server:init`
