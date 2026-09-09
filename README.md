# Pixeltable MCP Server (moved)

> **This repository is no longer maintained.**
> The Pixeltable MCP server now lives at
> **[pixeltable/mcp-server-pixeltable-developer](https://github.com/pixeltable/mcp-server-pixeltable-developer)**.

That is the server to install if you want Pixeltable available to Claude Code, Claude Desktop,
Cursor, or any other MCP client: 35 tools, 13 resources, and 11 prompts covering catalog
management, AI/ML pipelines, dependency installation, project scaffolding, and a persistent
Python REPL.

## Install the maintained server

Requires [`uv`](https://docs.astral.sh/uv/getting-started/installation/):

```bash
uv tool install --from git+https://github.com/pixeltable/mcp-server-pixeltable-developer.git mcp-server-pixeltable-developer
claude mcp add pixeltable mcp-server-pixeltable-developer   # Claude Code
```

Claude Desktop, Cursor, and from-source configuration are covered in the
[new repository's README](https://github.com/pixeltable/mcp-server-pixeltable-developer#readme).

File issues and feature requests at
[mcp-server-pixeltable-developer/issues](https://github.com/pixeltable/mcp-server-pixeltable-developer/issues).

## What used to be here

`servers/` still holds the original Docker Compose prototype: four separate index servers for
audio, video, images, and documents, plus a base SDK server. It is kept for reference only. It
targets an older Pixeltable release, receives no updates, and is superseded by the single
server above.

<details><summary>Original instructions</summary>

```bash
pip install pixeltable
git clone https://github.com/pixeltable/pixeltable-mcp-server.git
cd pixeltable-mcp-server/servers
docker-compose up --build     # audio 8080, video 8081, image 8082, doc 8083
docker-compose down
```

</details>

## Links

- [Pixeltable docs](https://docs.pixeltable.com)
- [Pixeltable on GitHub](https://github.com/pixeltable)
- [Discord community](https://discord.gg/pixeltable)

## License

Apache 2.0.
