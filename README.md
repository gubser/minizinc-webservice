# Dockerfile for building gecode and minizinc from source.

# Build & Run
```
docker build . -t minizinc
docker run -p 5004:80 minizinc
```

Then perform a POST request to http://localhost:5004/minizinc with the following body:
```
{
	"problem": "int: budget;\nvar 0..1000: F;\nvar 0..400: L;\nvar 0..500: Z;\nvar 0..150: J;\n\nconstraint 13*F + 21*L + 17*Z + 100*J <= budget;\n\nsolve maximize 6*F + 10*L + 8*Z + 40*J;\n",
	"data": {"budget": "10000"},
	"args": ["--output-mode", "json", "--output-objective"],
	"timeout_ms": 10000
}
```

# Testing
```
docker build . -t minizinc && docker run --rm minizinc python3 -m pytest /opt
```

TODO: run a never ending script and check if timeout is respected


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

TODO: What's missing is to make minizinc available as a web service.

## Additional files included in this repository
To simplify creation of the Docker image, some archives have been added to this repository which have their own LICENSE files.

The files were downloaded using:

libminizinc-2.2.3-source.tar.gz: `wget https://github.com/MiniZinc/libminizinc/archive/2.2.3.tar.gz -O libminizinc-2.2.3-source.tar.gz`

gecode-6.1.0-source.tar.gz: `wget https://github.com/Gecode/gecode/archive/release-6.1.0.tar.gz -O gecode-6.1.0-source.tar.gz`

minizinc-gecode-2.2.3.tar.gz contains the files under `/MiniZincIDE-2.2.3-bundle-linux/share/minizinc/gecode` of `https://github.com/MiniZinc/MiniZincIDE/releases/download/2.2.3/MiniZincIDE-2.2.3-bundle-linux-x86_64.tgz`

## Hints
To get minizinc to work we need some files (gecode.msc, minizinc-gecode-2.2.3.tar.gz) from the binary distribution of MiniZincIDE. (See https://github.com/MiniZinc/libminizinc/issues/228)
