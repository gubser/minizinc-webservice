FROM ubuntu:bionic AS base
RUN apt-get update && apt-get install -y \
    bison \
    flex

#
# build stage
FROM base AS build
RUN apt-get update && apt-get install -y \
    cmake \
    g++ \
    libmpfr-dev

# build gecode
WORKDIR /src
ADD gecode-6.1.0-source.tar.gz /src/

WORKDIR /src/gecode-release-6.1.0
RUN ./configure --disable-examples --disable-gist
RUN make
RUN make install

# build minizinc
WORKDIR /src
ADD libminizinc-2.2.3-source.tar.gz /src/

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
