# 🎵 MCP Server for Pixeltable

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/License-Apache_2.0-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Status-Alpha-orange.svg" alt="Status">
</p>

This repository contains server implementations for Pixeltable, providing tools that LLMs can invoke based on natural language queries.

## 📂 Repository Structure

```
mcp-server-pixeltable/
├── servers/
│   ├── audio-index/         # Audio indexing and querying service
│   │   ├── server.py        # Main server implementation
│   │   ├── tools.py         # Audio processing tools
│   │   ├── test.py          # Test scripts
│   │   ├── requirements.txt # Dependencies
│   │   └── Dockerfile       # Container configuration
│   │
│   └── base-sdk/            # Base SDK implementation
│       ├── server.py        # Main server implementation
│       ├── tools.py         # Core SDK tools
│       ├── requirements.txt # Dependencies
│       └── Dockerfile       # Container configuration
```

## 🚀 Available Servers

### Audio Index Server

Located in `servers/audio-index/`, this server provides:
- Audio file indexing with OpenAI Whisper transcription
- Semantic search capabilities for audio content
- Multi-index support for organizing audio collections

### Base SDK Server

Located in `servers/base-sdk/`, this server provides:
- Core functionality for Pixeltable integration
- Foundation for building specialized servers

## 📦 Installation

```bash
pip install pixeltable
git clone https://github.com/pixeltable/mcp-server-pixeltable.git
cd mcp-server-pixeltable
```

For specific server installation instructions, please refer to the README files in each server directory.

## 🔗 Links

- [Pixeltable GitHub](https://github.com/pixeltable/pixeltable)
- [Documentation](https://docs.pixeltable.io)
- [Discord Community](https://discord.gg/pixeltable)

## 📞 Support

- GitHub Issues: [Report bugs or request features](https://github.com/pixeltable/mcp-server-pixeltable/issues)
- Discord: Join our [community](https://discord.gg/pixeltable)