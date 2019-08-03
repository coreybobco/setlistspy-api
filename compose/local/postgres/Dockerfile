FROM postgres:10.5
WORKDIR /tmp
#Install Dexter to suggest indexes to speed up queries (requires HypoPG postgresql extension)
RUN apt-get update && apt install -y apt-transport-https curl make postgresql-server-dev-11 gcc wget
RUN curl -L https://github.com/HypoPG/hypopg/archive/1.1.2.tar.gz | tar xz && \
    cd hypopg-1.1.2 && make && make install
WORKDIR /
RUN wget -qO- https://dl.packager.io/srv/pghero/dexter/key | apt-key add - && \
    wget -O /etc/apt/sources.list.d/dexter.list https://dl.packager.io/srv/pghero/dexter/master/installer/debian/9.repo && \
    apt-get update && apt-get install dexter

COPY /compose/local/postgres/optimizations.sh /docker-entrypoint-initdb.d/optimizations.sh