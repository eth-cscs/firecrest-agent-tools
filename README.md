# CSCS Claude Code Plugins

Claude Code plugin marketplace for [CSCS](https://www.cscs.ch) services.

## Quick start

In [Claude Code](https://code.claude.com) (CLI, desktop app, or VS Code extension):

```
/plugin marketplace add ekouts/claude-plugins
/plugin install firecrest@cscs
```

## Available plugins

| Plugin | Description |
|---|---|
| [firecrest](./firecrest) | Access CSCS HPC systems through FirecREST via the hosted MCP server. See the [plugin README](./firecrest/README.md) for setup and authentication. |
| [firecrest-local](./firecrest-local) | Run the FirecREST MCP server locally in Docker with your own FirecREST client credentials — no hosted server required. See the [plugin README](./firecrest-local/README.md). |

## Using CSCS services outside Claude Code

Plugins only work in Claude Code. On the claude.ai webpage or the Claude Desktop
chat app, add the underlying MCP server as a **custom connector** instead — see the
[firecrest plugin README](./firecrest/README.md#claudeai-and-claude-desktop) for
instructions.

## For maintainers

Repository layout:

```
.claude-plugin/marketplace.json    # marketplace manifest: lists available plugins
firecrest/                         # one directory per plugin
├── .claude-plugin/plugin.json     # plugin manifest: name, version, metadata
├── .mcp.json                      # MCP server configuration (URL pointer)
├── skills/                        # skills bundled with the plugin
└── README.md
```

To ship an update: change the plugin, bump `version` in its `plugin.json`, and
push to `main`. Users pick the update up when their marketplace refreshes
(`/plugin marketplace update cscs`). There is no registry or publishing step.

Validate manifests locally before pushing (also enforced in CI):

```bash
claude plugin validate .
```

To test a plugin end-to-end from your working copy without publishing:

```
/plugin marketplace add /path/to/claude-plugins
/plugin install firecrest@cscs
```
