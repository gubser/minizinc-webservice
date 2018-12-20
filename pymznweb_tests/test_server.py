from aiohttp import web
# pylint: disable=E0401
from pymznweb.server import create_app

async def test_hello(aiohttp_client, loop):
    client = await aiohttp_client(create_app())

    resp = await client.get('/')
    assert resp.status == 200
    text = await resp.text()
    assert 'MiniZinc' in text

async def test_army_raw(aiohttp_client, loop):
    client = await aiohttp_client(create_app())

    resp = await client.post('/raw', json={
        "stdin": "int: budget;\nvar 0..1000: F;\nvar 0..400: L;\nvar 0..500: Z;\nvar 0..150: J;\n\nconstraint 13*F + 21*L + 17*Z + 100*J <= budget;\n\nsolve maximize 6*F + 10*L + 8*Z + 40*J;\n",
        "args": ["-Dbudget=10000", "--time-limit", "10000"]
    })

    assert resp.status == 200
    response = await resp.json()

    assert 'stdout' in response
    assert len(response['stderr']) == 0
    assert response['returncode'] == 0
    assert 'queueTimeMs' in response
    assert 'computeTimeMs' in response

    assert '==========' in response['stdout']

async def test_json(aiohttp_client, loop):
    client = await aiohttp_client(create_app())

    resp = await client.post('/json', json={
        "problem": "int: budget;\nvar 0..1000: F;\nvar 0..400: L;\nvar 0..500: Z;\nvar 0..150: J;\n\nconstraint 13*F + 21*L + 17*Z + 100*J <= budget;\n\nsolve maximize 6*F + 10*L + 8*Z + 40*J;\n",
        "data": { "budget": "10000" },
        "args": ["--output-objective"]
    })

    assert resp.status == 200
    response = await resp.json()

    print("response: ", response)

    assert response['result'] == 'complete'
    assert isinstance(response['values']['F'], int)
    assert "_objective" in response['values']

async def test_time_limit_too_short(aiohttp_client, loop):
    client = await aiohttp_client(create_app())

    resp = await client.post('/json', json={
        "problem": "int: budget;\nvar 0..1000: F;\nvar 0..400: L;\nvar 0..500: Z;\nvar 0..150: J;\n\nconstraint 13*F + 21*L + 17*Z + 100*J <= budget;\n\nsolve maximize 6*F + 10*L + 8*Z + 40*J;\n",
        "data": { "budget": "10000" },
        "args": ["--output-objective"],
        "timeoutMs": 1
    })

    assert resp.status == 200
    response = await resp.json()

    print("response: ", response)

    assert response['result'] == 'unknown'

async def test_unsatisfiable(aiohttp_client, loop):
    client = await aiohttp_client(create_app())

    request = {
        "problem": """
int: x;
int: y;

constraint x = y;
solve satisfy;
""",
        "data": { "x": "1", "y": "2" }
    }

    print("request: ", request)

    resp = await client.post('/json', json=request)

    assert resp.status == 200
    response = await resp.json()

    print("response: ", response)

    assert response['result'] == 'unsat'

async def test_unknown_data(aiohttp_client, loop):
    client = await aiohttp_client(create_app())

    request = {
        "problem": """
constraint 1 = 2;
solve satisfy;
""",
        "data": { "budget": "10000" }
    }

    resp = await client.post('/json', json=request)
    assert resp.status == 200
    response = await resp.json()
    assert response['result'] == 'error'
