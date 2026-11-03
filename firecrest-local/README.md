# FirecREST local plugin for Claude Code

Runs the FirecREST MCP server **locally in Docker** and connects Claude Code to
it. Unlike the [`firecrest`](../firecrest) plugin (which talks to a hosted
server), this variant needs no hosted infrastructure — you build the server
image from source and use your own FirecREST client credentials.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) running locally
- [Claude Code](https://code.claude.com) (CLI, desktop app, or VS Code extension)
- A clone of this repository: the server source is in [`firecrest-mcp/`](../firecrest-mcp)
- FirecREST OAuth client credentials (client id and secret) and the token/API
  URLs of the FirecREST deployment you use

## Setup

### 1. Build the server image

```bash
git clone https://github.com/eth-cscs/firecrest-agent-tools.git
cd firecrest-agent-tools/firecrest-mcp
docker compose build        # produces the image tagged "firecrest-mcp"
```

### 2. Export your credentials

In the shell you start Claude Code from (for example in `~/.zshrc`, or a
dedicated env file you `source`). If you already filled in
`firecrest-mcp/.env` for the server, export the same values with:

```bash
set -a; source firecrest-mcp/.env; set +a
```

Otherwise:

```bash
export OAUTH_CLIENT_ID=<your-client-id>
export OAUTH_CLIENT_SECRET=<your-client-secret>
export OAUTH_TOKEN_URL=https://<your-idp>/.../protocol/openid-connect/token
export OAUTH_SCOPES=firecrest-v2
export BACKEND_API_BASE_URL=<your-firecrest-url>
```

> Your credentials never leave your machine: Claude Code passes them to the
> local Docker container, which uses them to talk to FirecREST directly.
>
> **Note:** if FirecREST or your IdP also run in local Docker containers (e.g.
> the FirecREST demo environment), use `http://host.docker.internal:<port>` in
> the URLs instead of `http://localhost:<port>` — inside the server container,
> `localhost` is the container itself.

### 3. Install the plugin

Start `claude` from that shell, then:

```
/plugin marketplace add eth-cscs/firecrest-agent-tools
/plugin install firecrest-local@cscs
```

### 4. Verify

`/mcp` should show `firecrest · ✔ connected`. Then try:

```
> Which HPC systems are available?
> What's the status of job <id> on <system>?
```

## How it works

Claude Code starts a fresh container for each session with
`docker run --rm -i firecrest-mcp ... --transport stdio`, forwarding the five
`OAUTH_*`/`BACKEND_*` environment variables into it, and talks MCP over
stdin/stdout. The container is removed when the session ends.

To use a different image (e.g. one from a registry, or a differently named
local build), set `FIRECREST_MCP_IMAGE` before starting Claude Code:

```bash
export FIRECREST_MCP_IMAGE=firecrest-mcp:dev
```

## Notes

- All operations use the identity behind your client credentials.
- The server exposes the tools listed in the
  [server README](../firecrest-mcp/README.md#tools). In short: system status,
  job monitoring and file inspection, plus **job submission, cancellation and
  attaching a command to a running job**, and downloading a file into the
  container. Tools that modify the remote file system (mkdir, move, copy,
  remove, upload, chmod, chown, compress, extract) are present in the source
  but disabled.
- Over stdio the server also exposes `get_request_stats` and
  `reset_request_stats`, which show how many requests the server has sent to
  FirecREST in this session (needs a pyfirecrest release newer than 3.10.0 in
  the image). The last 1000 requests are kept; export
  `REQUEST_STATS_MAX_RECORDS` before starting Claude Code to change that (`0`
  keeps all of them).
- After changing the server source, rebuild with `docker compose build`; new
  Claude Code sessions pick up the new image automatically.

## Troubleshooting

- `/mcp` shows a connection error: check Docker is running, the image exists
  (`docker images | grep firecrest-mcp`), and the five environment variables
  are set in the shell where you started Claude Code (`env | grep -E 'OAUTH|BACKEND'`).
- Tool calls fail with authentication errors: test your credentials by hand —

  ```bash
  curl -s -X POST "$OAUTH_TOKEN_URL" \
    -d grant_type=client_credentials \
    -d client_id="$OAUTH_CLIENT_ID" \
    -d client_secret="$OAUTH_CLIENT_SECRET" \
    -d scope="$OAUTH_SCOPES"
  ```

  should return an `access_token`.
