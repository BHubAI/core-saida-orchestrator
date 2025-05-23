<p align="center">
    <a href="https://github.com/rafaelnunes/core-saida-orchestrator/actions">
        <img alt="GitHub Actions status" src="https://github.com/rafaelnunes/core-saida-orchestrator/actions/workflows/main.yml/badge.svg">
    </a>
    <a href="https://github.com/rafaelnunes/core-saida-orchestrator/releases"><img alt="Release Status" src="https://img.shields.io/github/v/release/rafaelnunes/core-saida-orchestrator"></a>
</p>

# core-saida-orchestrator

## Architecture

<p align="center">
    <a href="#">
        <img alt="Architecture Workflow" src="https://i.imgur.com/8TEpVZk.png">
    </a>
</p>

## Usage

1. `make up`
2. visit `http://localhost:8666/v1/ping` for uvicorn server, or `http://localhost` for nginx server
3. Backend, JSON based web API based on OpenAPI: `http://localhost/v1/`
4. Automatic interactive documentation with Swagger UI (from the OpenAPI backend): `http://localhost/docs`

## Backend local development, additional details

Initialize first migration (project must be up with docker compose up and contain no 'version' files)

```shell
$ make alembic-init
```

Create new migration file

```shell
$ docker compose exec backend alembic revision --autogenerate -m "some cool comment"
```

Apply migrations

```shell
$ make alembic-migrate
```

### Migrations

Every migration after that, you can create new migrations and apply them with

```console
$ make alembic-make-migrations "cool comment dude"
$ make alembic-migrate
```

### General workflow

See the [Makefile](/Makefile) to view available commands.

By default, the dependencies are managed with [Poetry](https://python-poetry.org/), go there and install it.

From `./backend/` you can install all the dependencies with:

```console
$ poetry install
```

### pre-commit hooks

If you haven't already done so, download [pre-commit](https://pre-commit.com/) system package and install. Once done, install the git hooks with

```console
$ pre-commit install
pre-commit installed at .git/hooks/pre-commit
```

### Nginx

The Nginx webserver acts like a web proxy, or load balancer rather. Incoming requests can get proxy passed to various upstreams eg. `/:service1:8001,/static:service2:8002`

```yml
volumes:
  proxydata-vol:
---
nginx:
  image: your-registry/nginx
  # OR you can do the following
  # build:
  #   context: ./nginx
  #   dockerfile: ./Dockerfile
  environment:
    - UPSTREAMS=/:backend:8000
    - NGINX_SERVER_NAME=yourservername.com
    - ENABLE_SSL=true
    - HTTPS_REDIRECT=true
    - CERTBOT_EMAIL=youremail@gmail.com
    - DOMAIN_LIST=yourservername.com
    - BASIC_AUTH_USER=user
    - BASIC_AUTH_PASS=pass
  ports:
    - "0.0.0.0:80:80"
    - "0.0.0.0:443:443"
  volumes:
    - proxydata-vol:/etc/letsencrypt
```

Some of the environment variables available:

- `UPSTREAMS=/:backend:8000` a comma separated list of \<path\>:\<upstream\>:\<port\>. Each of those of those elements creates a location block with proxy_pass in it.
- `HTTPS_REDIRECT=true` enabled a standard, ELB compliant https redirect.
- `ENABLE_SSL=true` to enable redirects to https from http
- `NGINX_SERVER_NAME` name of the server and used as path name to store ssl fullchain and privkey
- `CERTBOT_EMAIL=youremail@gmail.com` the email to register with Certbot.
- `DOMAIN_LIST` domain(s) you are requesting a certificate for.
- `BASIC_AUTH_USER` username for basic auth.
- `BASIC_AUTH_PASS` password for basic auth.

When SSL is enabled, server will install Cerbot in standalone mode and add a new daily periodic script to `/etc/periodic/daily/` to run a cronjob in the background. This allows you to automate cert renewing (every 3 months). See [docker-entrypoint](nginx/docker-entrypoint.sh) for details.

### Deployments

A common scenario is to use an orchestration tool, such as docker swarm, to deploy your containers to the cloud (DigitalOcean). This can be automated via GitHub Actions workflow. See [main.yml](/.github/workflows/main.yml) for more.

You will be required to add `secrets` in your repo settings:

- DIGITALOCEAN_TOKEN: your DigitalOcean api token
- REGISTRY: container registry url where your images are hosted
- POSTGRES_PASSWORD: password to postgres database
- STAGING_HOST_IP: ip address of the staging droplet
- PROD_HOST_IP: ip address of the production droplet
- SSH_KEY: ssh key of user connecting to server (`ubuntu` in this case)
