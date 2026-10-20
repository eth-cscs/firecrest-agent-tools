# FirecREST Agent Tools

Tools for using [FirecREST](https://products.cscs.ch/#/product/firecrest), the REST API to CSCS HPC systems, from AI agents and coding assistants.

FirecREST exposes Slurm job management, file system access, and system status over HTTP.
This repository collects the integrations that let agents such as Claude Code use those capabilities: MCP server configuration, agent plugins, and skills that encode HPC know-how (for example, how to diagnose a pending or failed Slurm job).

## What is here

| Component | Description |
|---|---|
| Claude Code plugins | A plugin marketplace (`cscs`) with plugins that connect Claude Code to FirecREST, either through the hosted MCP server or a locally run one. |
| Skills | Task-oriented instructions bundled with the plugins, such as monitoring a Slurm job and inspecting its output. |

More agent frameworks and standalone skill files may be added over time.

## Quick start (Claude Code)

In [Claude Code](https://code.claude.com) (CLI, desktop app, or VS Code extension):

```
/plugin marketplace add eth-cscs/firecrest-agent-tools
/plugin install firecrest@cscs
```

The `firecrest` plugin points Claude Code at the hosted FirecREST MCP server at `https://mcp.firecrest.cscs.ch/mcp` and authenticates with your CSCS account.
The `firecrest-local` plugin runs the MCP server in Docker on your machine with your own FirecREST client credentials.
See each plugin's README for setup details.

## Using FirecREST outside Claude Code

Plugins only work in Claude Code. On claude.ai or in the Claude Desktop chat app, add the FirecREST MCP server as a custom connector instead, using the server URL above.

## Repository layout

```
.claude-plugin/marketplace.json    # Claude Code marketplace manifest (must live at the repo root)
firecrest/                         # Claude Code plugin: hosted MCP server + skills
firecrest-local/                   # Claude Code plugin: MCP server in local Docker
.github/workflows/                 # CI: validates the marketplace and plugin manifests
```

Each plugin directory contains a `.claude-plugin/plugin.json` manifest, an `.mcp.json` with the MCP server configuration, an optional `skills/` directory, and a README.

## For maintainers

To ship a plugin update: change the plugin, bump `version` in its `plugin.json`, and merge to `main`.
Users pick the update up when their marketplace refreshes (`/plugin marketplace update cscs`).
There is no registry or publishing step.

Validate manifests locally before opening a pull request:

```bash
claude plugin validate .
```

To test a plugin end-to-end from a working copy:

```
/plugin marketplace add /path/to/firecrest-agent-tools
/plugin install firecrest@cscs
```
