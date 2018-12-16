# Dockerfile for building gecode and minizinc from source.

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
