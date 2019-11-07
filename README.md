# A simple web API providing MiniZinc + Gecode in a Docker container

# Build & Run
```
docker build . -t minizinc --build-arg NUM_BUILD_JOBS=4
docker run -p 5004:80 minizinc
```

In the following we let the service compute the solution for the following MiniZinc problem (with parameter budget set to 10000):
```
int: budget;
var 0..1000: F;
var 0..400: L;
var 0..500: Z;
var 0..150: J;

constraint 13*F + 21*L + 17*Z + 100*J <= budget;

solve maximize 6*F + 10*L + 8*Z + 40*J;
```

Running the following:
```
curl -H "Content-Type: application/json" -X POST -d '{
	"problem": "int: budget;\nvar 0..1000: F;\nvar 0..400: L;\nvar 0..500: Z;\nvar 0..150: J;\n\nconstraint 13*F + 21*L + 17*Z + 100*J <= budget;\n\nsolve maximize 6*F + 10*L + 8*Z + 40*J;\n",
	"data": {"budget": "10000"},
	"args": ["--output-mode", "json", "--output-objective"],
	"timeout_ms": 10000
}' http://localhost:5004/json
```

Will yield:
```json
{
	"result": "complete",
	"values": {
		"F": 0, 
		"L": 392, 
		"Z": 104, 
		"J": 0, 
		"_objective": 4752
	}, 
	"stdout": "{\n  \"F\" : 0,\n  \"L\" : 392,\n  \"Z\" : 104,\n  \"J\" : 0,\n  \"_objective\" : 4752\n}\n----------\n==========\n", 
	"stderr": "", 
	"returncode": 0, 
	"queueTimeMs": 0, 
	"computeTimeMs": 84
}
```

# How to use
The service provides three endpoints, an echo service for a simple health check, a high-level endpoint that does some parsing and a low-level endpoint that is basically a pass-through.

Its hard-coded to 10 concurrent jobs. If more jobs arrive, they will be queued. Default timeout is 30s. You can change these values in [pymznweb/server.py](pymznweb/server.py).

 - `GET /`
    
	Will return `MiniZinc` as plain text (echo service)

 - `POST /json`
 
 	Call it with a JSON of the following form:
    ```json
	{
		"problem": "
			int: budget;
			var 0..1000: F;
			var 0..400: L;
			var 0..500: Z;
			var 0..150: J;

			constraint 13*F + 21*L + 17*Z + 100*J <= budget;

			solve maximize 6*F + 10*L + 8*Z + 40*J;
		",
		"data": {
			"budget": "10000"
		},
		"args": <optional command line arguments>,
		"timeoutMs": <optional computing timeout>,
	}
	```

	The output will be:

	```json
	{
		"result": "complete",
		"values": {
			"F": 0, 
			"L": 392, 
			"Z": 104, 
			"J": 0, 
			"_objective": 4752
		}, 
		"stdout": "{\n  \"F\" : 0,\n  \"L\" : 392,\n  \"Z\" : 104,\n  \"J\" : 0,\n  \"_objective\" : 4752\n}\n----------\n==========\n", 
		"stderr": "", 
		"returncode": 0, 
		"queueTimeMs": 0, 
		"computeTimeMs": 84
	}
	```

	Where `result` can be 
	- `unsat` ⇨ Unsatisfyable, no solution was found
	- `unbounded` ⇨ Too few constraints
	- `unsatOrUnbounded`
	- `unknown` ⇨ Timed out before solution was found
	- `error` ⇨ Error, check the contents of `stderr`
	- `complete` ⇨ An optimal solution was found
	- `found` ⇨ A satisfying solution was found


 - `POST /raw`
    
	A more low-level approach. Call this endpoint with a JSON of command line `args` and `stdin`. These values will be given to MiniZinc as is.
    ```json
	{
		"args": "<command line arguments>",
		"stdin": "<MiniZinc problem code>"
	}
	```

	The output will be:
	```json
	{
		"stdout": "",
		"stderr": "",
		"returncode": 0,
		"queueTimeMs": 100,
		"computeTimeMs": 20
	}
	```


# Testing
```
docker build . -t minizinc && docker run --rm minizinc python3 -m pytest /opt
```


# Shell-Only

Usage example:
```
$ docker build . -t minizinc
$ docker run -it minizinc bash

# apt-get install -y nano
# nano army.mzn
<insert army.mzn>
# minizinc model.mzn
F = 0, L = 392, Z=104, J = 0
----------
==========
```

(The source code for army.mzn is available from https://github.com/MiniZinc/specialization-examples/blob/master/introduction/army/army.mzn)

## Additional files included in this repository
To get minizinc to work we need some files (gecode.msc, minizinc-gecode-2.2.3.tar.gz) from the binary distribution of MiniZincIDE. (See https://github.com/MiniZinc/libminizinc/issues/228)

minizinc-gecode-2.2.3.tar.gz contains the files under `/MiniZincIDE-2.2.3-bundle-linux/share/minizinc/gecode` of `https://github.com/MiniZinc/MiniZincIDE/releases/download/2.2.3/MiniZincIDE-2.2.3-bundle-linux-x86_64.tgz`. They are needed for useful execution of MiniZinc.

