# Multimodal Model Context Protocal Server

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/License-Apache_2.0-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Status-Beta-yellow.svg" alt="Status">
</p>

This repository contains a collection of server implementations for Pixeltable, designed to handle multimodal data indexing and querying (audio, video, images, and documents). These services are orchestrated using Docker for local development.

## 🚀 Available Servers

### Audio Index Server
Located in `servers/audio-index/`, this server provides:
- Audio file indexing with transcription capabilities
- Semantic search over audio content
- Multi-index support for audio collections
- Accessible at `/audio` endpoint

### Video Index Server
Located in `servers/video-index/`, this server provides:
- Video file indexing with frame extraction
- Content-based video search
- Accessible at `/video` endpoint

### Image Index Server
Located in `servers/image-index/`, this server provides:
- Image indexing with object detection
- Similarity search for images
- Accessible at `/image` endpoint

### Document Index Server
Located in `servers/doc-index/`, this server provides:
- Document indexing with text extraction
- Retrieval-Augmented Generation (RAG) support
- Accessible at `/doc` endpoint

### Base SDK Server
Located in `servers/base-sdk/`, this server provides:
- Core functionality for Pixeltable integration
- Foundation for building specialized servers

## 📦 Installation

### Local Development
```bash
pip install pixeltable
git clone https://github.com/pixeltable/mcp-server-pixeltable.git

cd mcp-server-pixeltable/servers

docker-compose up --build                 # Run locally with docker-compose
docker-compose down                       # Take down resources
```

## 🔧 Configuration
- Each service runs on its designated port (8080 for audio, 8081 for video, 8082 for image, 8083 for doc).
- Configure service settings in the respective Dockerfile or through environment variables.

## 🔗 Links
- [Pixeltable GitHub](https://github.com/pixeltable)
- [Pixeltable Documentation](https://docs.pixeltable.com)
- [Discord Community](https://discord.gg/pixeltable)

## 📞 Support
- GitHub Issues: [Report bugs or request features](https://github.com/pixeltable/mcp-server-pixeltable/issues)
- Discord: Join our [community](https://discord.gg/pixeltable)

## 📜 License
This project is licensed under the Apache 2.0 License.