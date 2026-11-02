# MCP for FirecREST

## Run a Docker instance

> Note: This is a local instance, we aim to produce an MCP that runs in a public environment as an MCP server (ie, `https://mcp.firecrest.cscs.ch`) able to be used in a plugin.

1. Install (if you don't have it yet) docker compose
2. Clone this repository, go to the base path, copy the file `.env.tmp` into `.env`, and change the following values according to your FirecREST configuration in `.env`:

    - `OAUTH_CLIENT_ID`: Client ID
    - `OAUTH_CLIENT_SECRET`: Client Secret
    - `OAUTH_TOKEN_URL`: Token endpoint of your IdP (usually it finishes in `/token`)
    - `BACKEND_API_BASE_URL`: FirecREST URL

    > Warning: remember the Client Id and Secret are sensitive data. Don't expose this in any repository or forum.

    Save the file, and

3. Execute `docker compose`:

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
