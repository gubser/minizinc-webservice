FROM ubuntu:bionic AS build
RUN apt-get update && apt-get install -y \
    cmake \
    g++ \
    libmpfr-dev \
    bison \
    flex \
    python3 \
    python3-pip && \
    rm -rf /var/lib/apt/lists/*

# build gecode
WORKDIR /src
ADD gecode-6.1.0-source.tar.gz /src/

WORKDIR /src/gecode-release-6.1.0
RUN ./configure --disable-examples
RUN make -j 4
RUN make install

# build minizinc
WORKDIR /src
ADD libminizinc-2.2.3-source.tar.gz /src/

WORKDIR /src/libminizinc-2.2.3/build
RUN cmake -DGECODE_HOME="/src/gecode-release-6.1.0/gecode" ..
RUN cmake --build . -- -j 4
RUN cmake --build . --target install

# update shared libraries cache
RUN ldconfig

# add auxiliary gecode and minizinc files
ADD Preferences.json /usr/local/share/minizinc/Preferences.json
ADD gecode.msc /usr/local/share/minizinc/solvers/
ADD minizinc-gecode-2.2.3.tar.gz /usr/local/share/minizinc/

# cleanup
WORKDIR /
RUN rm -r /src

WORKDIR /opt/pymznweb
ADD pymznweb/requirements.txt /opt/pymznweb/requirements.txt
RUN pip3 install -r requirements.txt

ADD pymznweb /opt/pymznweb
CMD [ "python3", "server.py" ]
