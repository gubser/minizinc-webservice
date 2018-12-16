FROM ubuntu:bionic AS build
RUN apt-get update && apt-get install -y unzip cmake g++ libmpfr-dev bison flex

# build gecode
WORKDIR /src
ADD gecode-6.1.0-source.zip /src/gecode.zip
RUN unzip -q gecode.zip

WORKDIR /src/gecode-release-6.1.0
RUN ./configure --disable-examples
RUN make -j 2
RUN make install

# build minizinc
WORKDIR /src
ADD libminizinc-2.2.3-source.zip /src/libminizinc.zip
RUN unzip -q libminizinc.zip

WORKDIR /src/libminizinc-2.2.3/build
RUN cmake -DGECODE_HOME="/src/gecode-release-6.1.0/gecode" ..
RUN cmake --build . -- -j 4
RUN cmake --build . --target install

# update shared libraries cache
RUN ldconfig

# add auxiliary gecode and minizinc files
ADD Preferences.json /usr/local/share/minizinc/Preferences.json
ADD gecode.msc /usr/local/share/minizinc/solvers/
ADD gecode-minizincide-2.2.3 /usr/local/share/minizinc/gecode

# create runtime image
##FROM ubuntu:bionic AS runtime
##WORKDIR /app/minizinc
##COPY --from=build /app/minizinc .
##ENV PATH="${PATH}:/app/minizinc/bin"
#ENTRYPOINT ["minizinc"]
