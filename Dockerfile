FROM ubuntu:bionic AS base
RUN apt-get update && apt-get install -y \
    bison \
    flex

#
# build stage
FROM base AS build
ARG NUM_BUILD_JOBS=1
RUN apt-get update && apt-get install -y \
    cmake \
    g++ \
    libmpfr-dev

# retrieve gecode and minizinc
# (if you want to bump version, make sure you update
# minizinc-gecode-2.2.3.tar.gz as well (see README.md))
WORKDIR /src
ADD https://github.com/MiniZinc/libminizinc/archive/2.2.3.tar.gz libminizinc-2.2.3-source.tar.gz
RUN tar -xf libminizinc-2.2.3-source.tar.gz

ADD https://github.com/Gecode/gecode/archive/release-6.1.0.tar.gz gecode-6.1.0-source.tar.gz
RUN tar -xf gecode-6.1.0-source.tar.gz

# build gecode
WORKDIR /src/gecode-release-6.1.0
RUN ./configure --disable-examples --disable-gist
RUN make -j ${NUM_BUILD_JOBS}
RUN make install

# build minizinc
WORKDIR /src/libminizinc-2.2.3/build
RUN cmake -DGECODE_HOME="/src/gecode-release-6.1.0/gecode" ..
RUN cmake --build .
RUN cmake --build . --target install

# add auxiliary gecode and minizinc files
ADD Preferences.json /usr/local/share/minizinc/Preferences.json
ADD gecode.msc /usr/local/share/minizinc/solvers/
ADD minizinc-gecode-2.2.3.tar.gz /usr/local/share/minizinc/

#
# runtime stage
FROM base AS runtime
RUN apt-get update && apt-get install -y \
    python3 \
    python3-aiohttp \
    python3-pytest

# copy build results
COPY --from=build /usr/local /usr/local

# update shared libraries cache
RUN ldconfig

# add server script
ADD pymznweb /opt/pymznweb
ADD pymznweb_tests /opt/pymznweb_tests
WORKDIR /opt
EXPOSE 80
CMD [ "python3", "-m", "aiohttp.web", "-H", "*", "-P", "80", "pymznweb.server:create_app"]
