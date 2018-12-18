from aiohttp import web
from typing import Dict
import json
import asyncio

NUM_CONCURRENT_JOBS = 10
TIMEOUT_MS = 30000


sem = asyncio.Semaphore(NUM_CONCURRENT_JOBS)

async def handle(request: web.Request):
    try:
        await sem.acquire()

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

        if 'timeout_ms' in req:
            timeout_ms = req['timeout_ms']
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
        
        # send back
        res = {
            'stdout': stdout.decode(),
            'stderr': stderr.decode(),
            'returncode': proc.returncode
        }

        return web.Response(text=json.dumps(res), content_type='application/json')
    finally:
        sem.release()

def main():
    app = web.Application()
    app.add_routes([web.post('/', handle)])

    web.run_app(app)

if __name__ == "__main__":
    main()