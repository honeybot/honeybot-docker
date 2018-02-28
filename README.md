# honeybot in docker

This repository explains how to build and use honeybot-agent docker container

## Start container from Docker Hub

To start honeybot following environment variable should be specified

| Variable | Mandatory | Description |
| -------- | --------- | ----------- |
| HB_ID | Yes | Identifier of agent instance |
| HB_GROUPID | Yes | Identifier of policies goup, related to this agent |
| HG_HOST | Yes | Management server hostname/address |
| HG_KEY | Yes | Pre-shared secret to authenticate on management server |
| SSL_HOST | No | If specified, letsencrypt will try to get SSL-certificate for hostname set |



Example usage:
```
docker run --name honeybot -e HB_ID="agent-01" -e SSL_HOST=agent.test.server.com -e HB_GROUPID=aaabbbccc111 -e HG_HOST=management.server.com -e HG_KEY=aaaaaaabbbbbbbcccccc1111111 -p 80:80 -p 443:443 -d honeybot/honeybot
```

## Build from Dockerfile
```
docker build . -t honeybot/honeybot -f Dockerfile
```
