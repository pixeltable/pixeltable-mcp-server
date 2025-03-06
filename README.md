# Pixeltable MCP Server

This is a simple MCP (Model-Client-Protocol) server that wraps around the Pixeltable SDK, providing a convenient API for working with Pixeltable's multimodal data infrastructure.

## Clone the repo
`gh repo clone pixeltable/mcp-server-pixeltable`

## Installation

```bash
pip install pixeltable mcp
```

## Add the tool to cursor
1. Go to cursor settings
2. Add MCP > Add Name > Type = 'Command'
3. Command: `python ~\mcp-server-pixeltable\server.py`

Note this assumes you install at the global python level.