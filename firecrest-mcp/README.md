# MCP for FirecREST

An [MCP](https://modelcontextprotocol.io) server that gives AI agents access to
HPC systems through [FirecREST](https://products.cscs.ch/#/product/firecrest),
built on [pyfirecrest](https://github.com/eth-cscs/pyfirecrest) and
[FastMCP](https://gofastmcp.com). It is the server run by the
[`firecrest-local`](../firecrest-local) Claude Code plugin.

All tools act with the identity behind the OAuth client credentials the server
is configured with.

## Tools

- **Systems**: `get_server_version`, `get_systems`, `get_nodes`,
  `get_partitions`, `get_reservations`, `get_userinfo`.
- **Files (read)**: `list_files`, `head_file`, `tail_file`, `view_file`,
  `get_checksum`, `get_file_type`, `stat_path`, and `download_file` (saves a
  remote file to a path inside the server's container).
- **Jobs**: `get_job_status`, `get_job_metadata`, `wait_for_job`, and the
  tools that change the scheduler state: `submit_job`, `cancel_job`,
  `attach_to_job`.
- **Request statistics** (stdio transport only): `get_request_stats`,
  `reset_request_stats`; see below.

Tools that modify the remote file system (`chmod`, `chown`, `mkdir`,
`create_symlink`, `move_path`, `copy_path`, `remove_path`, `upload_file`,
`compress_path`, `extract_archive`) are implemented in `src/server.py` but
commented out, so they are not exposed.

## Run a Docker instance

> Note: This is a local instance, we aim to produce an MCP that runs in a public environment as an MCP server (ie, `https://mcp.firecrest.cscs.ch`) able to be used in a plugin.

1. Install (if you don't have it yet) docker compose
2. Clone this repository, go to this directory (`firecrest-mcp/`), and create a `.env` file with the following values according to your FirecREST configuration:

    - `OAUTH_CLIENT_ID`: Client ID
    - `OAUTH_CLIENT_SECRET`: Client Secret
    - `OAUTH_TOKEN_URL`: Token endpoint of your IdP (usually it finishes in `/token`)
    - `OAUTH_SCOPES`: Scopes to request, e.g. `firecrest-v2`
    - `BACKEND_API_BASE_URL`: FirecREST URL
    - `REQUEST_STATS_MAX_RECORDS` (optional): see [Request statistics](#request-statistics)

    > Warning: remember the Client Id and Secret are sensitive data. Don't expose this in any repository or forum.

    Save the file, and

3. Execute `docker compose`. This runs the server over HTTP on port 8888; the
   `firecrest-local` plugin instead starts the same image with
   `--transport stdio` for each Claude Code session.

```bash
$ cd /path/to/this/repo
$ docker compose up --build
+] up 2/2
 ✔ Network firecrest-mcp_default        Created                                                              0.0s
 ✔ Container firecrest-mcp-mcp-server-1 Created                                                              0.0s
Attaching to mcp-server-1
mcp-server-1  | Using CPython 3.13.14 interpreter at: /usr/local/bin/python3
mcp-server-1  | Creating virtual environment at: .venv
(...)
mcp-server-1  | INFO:     Started server process [78]
mcp-server-1  | INFO:     Waiting for application startup.
mcp-server-1  | INFO:     Application startup complete.
mcp-server-1  | INFO:     Uvicorn running on http://0.0.0.0:8888 (Press CTRL+C to quit)
```

## Test local instance with Claude Code

Add the MCP to your local claude code environment by using the `claude mcp add` command:

```bash
$ claude mcp add firecrest http://localhost:8888/mcp --transport http
$ claude
> /mpc
  Manage MCP servers
  3 servers

    Local MCPs (/Users/username/.claude.json [project: /Users/username/dev/firecrest-mcp])
  ❯ firecrest · ✔ connected
```

## Test local instance in Claude Desktop

For this, we need to configure the Claude Desktop before starting.

Edit the following `claude_desktop_config.json` file, and add this under `mcpServers` field.

> Note: Claude Desktop Config file can be found in Linux systems in `~/.config/Claude/claude_desktop_config.json` and in MacOS desktops in `~/Library/Application\ Support/Claude/claude_desktop_config.json`

```json
    {
      "mcpServers": {
         "firecrest": { 
           "command": "npx",
           "args": [
             "mcp-remote",
             "http://localhost:8888/mcp",
             "--transport", "http-only",
             "--allow-http"
           ]
         }
      },
      (...)
    }
```

Save the file, then, restart Claude Desktop so it loads the MCP server connection on your environment.

To confirm it's working, you can check on Settings -> Developer and you should see the instance running.

## Request statistics

The server counts every HTTP request it sends to the FirecREST API (retries
included) using the `request_stats` of the pyfirecrest client
([pyfirecrest#223](https://github.com/eth-cscs/pyfirecrest/pull/223), in
pyfirecrest releases newer than 3.10.0). Each request is also logged at `INFO`
level, e.g.

```
INFO FirecREST request: GET /status/systems -> 200 (0.123s, attempt 0)
```

Two tools expose the statistics to the agent:

- `get_request_stats(last=20)`: the counters since the server started (total,
  retries, failed, durations, breakdowns by method, endpoint and status) and
  the `last` most recent requests with their method, endpoint, query
  parameters, outcome, timing and tracing IDs. No headers or bodies are
  recorded, so the access token never appears in the output.
- `reset_request_stats()`: clears the counters and the history.

The history keeps the last 1000 requests by default; set the
`REQUEST_STATS_MAX_RECORDS` environment variable (or `.env` entry) to change
that, with `0` keeping every request (memory then grows with the number of
requests). The counters are never truncated.

The counters are global to the server process, so the two tools are only
registered when the server runs over stdio (`--transport stdio`), where the
process serves a single Claude Code session. Over HTTP the process is shared by
all the users and the tools are not exposed; only the log lines are emitted.
With an older pyfirecrest the server still starts, logs a warning, and the
tools report `"enabled": false`.
