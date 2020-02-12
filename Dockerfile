# Dockerfile - HoneyBot

FROM debian:stretch

LABEL maintainer="Mikhail Golovanov <migolovanov@ptsecurity.com>"

RUN DEBIAN_FRONTEND=noninteractive apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        wget \
        gnupg2 \
        software-properties-common \
        python3-pip \
        python-pip \
        apt-utils \
        cron \
        git-core \
        make \
	build-essential \
	libreadline-dev \
    && wget -qO - https://openresty.org/package/pubkey.gpg | apt-key add - \
    && add-apt-repository -y "deb http://openresty.org/package/debian $(lsb_release -sc) openresty" \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
        openresty \
	lua5.1 \
	liblua5.1-dev \
	unzip \
        redis-server \
    && pip3 install \
        websockets \
        asyncio \
        redis \
    && wget https://luarocks.org/releases/luarocks-3.3.1.tar.gz \
    && tar zxpf luarocks-3.3.1.tar.gz \
    && cd luarocks-3.3.1 \
    && ./configure \
    && make build \
    && make install \
    && cd / \
    && rm -rf /luarocks-3.3.1 \
    && luarocks install wtf \
    && luarocks install wtf-honeybot-core \
    &&  sed -i "s/ngx.socket.tcp/require(\"socket.unix\")/g" /usr/local/openresty/lualib/resty/redis.lua \
    &&  sed -i "/if.*ULIMIT/,+4d" /etc/init.d/redis-server \
    &&  sed -i "s/^\(.*pam_loginuid.so\)/#\1/" /etc/pam.d/cron \
    && find /usr/local/openresty/lualib/resty/ -type f -exec sed -i "s/sock:send(req)/sock:send(table.concat(req))/g" {} \; \
    && sed -i "s/^bind/#bind/g" /etc/redis/redis.conf \
    && mkdir /var/run/redis \
    && mkdir -p /usr/local/openresty/nginx/html/.well-known/acme-challenge \
    && chown -R redis:www-data /var/run/redis \
    && echo "unixsocket /var/run/redis/redis.sock" >> /etc/redis/redis.conf \
    && echo "unixsocketperm 775" >> /etc/redis/redis.conf \
    && cd /etc/openresty \
    && git clone https://github.com/honeybot/wtf-demo-policy \
    && rm -fr wtf-demo-policy/policy/* \
    && cd /opt \
    && git clone https://github.com/certbot/certbot \
    && rm -fr /var/cache/apt/archives/* \


ENV PATH=$PATH:/usr/local/openresty/luajit/bin/:/usr/local/openresty/nginx/sbin/:/usr/local/openresty/bin/

COPY /client.py /opt/client.py
COPY /update.py /opt/update.py
COPY /nginx.conf /etc/openresty/nginx.conf
COPY /start.sh /

CMD ["/start.sh"]
