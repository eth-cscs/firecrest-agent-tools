# FirecREST plugin for Claude Code

Gives Claude access to CSCS HPC systems through the
[FirecREST](https://products.cscs.ch/#/product/firecrest) API: system and
partition status, job monitoring, and file inspection.

All operations run under **your** CSCS identity — you can only see the resources
your account can access. The current version exposes **read-only** tools; job
submission and file modification are not available through this plugin.

The plugin contains no code and no secrets: it connects Claude Code to the MCP
server hosted at CSCS (`https://mcp.firecrest.cscs.ch/mcp`), and you authenticate
with your own CSCS account through your browser.

## Installation

1. Add the CSCS marketplace (one-time):

   ```
   /plugin marketplace add ekouts/claude-plugins
   ```

2. Install the plugin:

   ```
   /plugin install firecrest@cscs
   ```

3. Authenticate: run `/mcp`, select `firecrest`, and choose **Authenticate**. A
   browser window opens — log in with your CSCS account. Claude Code stores the
   token in your OS keychain and refreshes it automatically.

4. Verify: `/mcp` should show `firecrest · ✔ connected`.

## Example prompts

```
> Which HPC systems are available right now?
> What's the state of the partitions on daint?
> Is my job 123456 on daint still running? Show me the last lines of its output file.
> List the files in /scratch/snx3000/<user>/run42 and show me the job script.
```

## What the tools can do

- **Systems**: list systems, nodes, partitions, and reservations; server version;
  your user information.
- **Jobs**: job status and metadata; wait for a job to finish.
- **Files**: list directories; `head`/`tail`/view files; file type, checksum, and
  `stat` information.

## claude.ai and Claude Desktop

Claude Code plugins do not run on the claude.ai webpage or the Claude Desktop chat
app. There, add the server as a **custom connector** instead (paid claude.ai plans):

1. **Settings → Connectors → Add custom connector**
2. URL: `https://mcp.firecrest.cscs.ch/mcp`
3. **Add**, then **Connect** and log in with your CSCS account.

On Team/Enterprise plans, an org admin can pre-configure the connector for the
whole organization under **Admin settings → Connectors**.

## Connecting to a different server (development)

The plugin honors the `FIRECREST_MCP_URL` environment variable, falling back to
the production URL when unset. To test against a locally running server:

```bash
export FIRECREST_MCP_URL=http://localhost:8888/mcp
claude
```

## Troubleshooting

- `/mcp` shows the server as failed or disconnected: check that you can reach
  the server URL from your network, then try **Reconnect** in `/mcp`.
- Authentication loops or expired sessions: in `/mcp`, select the server and
  choose **Clear authentication**, then authenticate again.
- To remove the plugin: `/plugin uninstall firecrest@cscs`.

## Support

Contact CSCS support via the [service desk](https://support.cscs.ch), or open an
issue in this repository.
