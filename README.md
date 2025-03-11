# 🎵 MCP Server for Pixeltable

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/License-Apache_2.0-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Status-Beta-yellow.svg" alt="Status">
  <img src="https://img.shields.io/badge/AWS_CDK-v2.x-blueviolet.svg" alt="AWS CDK">
</p>

This repository contains a collection of server implementations for Pixeltable, designed to handle multimodal data indexing and querying (audio, video, images, and documents). These services are orchestrated using Docker and deployed to AWS ECS with an Application Load Balancer (ALB) via AWS CDK.

## 📂 Repository Structure

```
mcp-server-pixeltable/
├── app.py                  # AWS CDK stack for ECS deployment
├── cdk.json                # CDK configuration file
├── requirements.txt        # CDK dependencies
├── servers/
│   ├── audio-index/         # Audio indexing and querying service
│   │   ├── Dockerfile      # Container configuration
│   │   ├── requirements.txt# Dependencies
│   │   ├── server.py       # Main server implementation
│   │   ├── test.py         # Test scripts
│   │   └── tools.py        # Audio processing tools
│   │
│   ├── video-index/         # Video indexing and querying service
│   │   ├── Dockerfile      # Container configuration
│   │   ├── requirements.txt# Dependencies
│   │   ├── server.py       # Main server implementation
│   │   └── test.py         # Test scripts
│   │
│   ├── image-index/         # Image indexing and querying service
│   │   ├── Dockerfile      # Container configuration
│   │   ├── requirements.txt# Dependencies
│   │   ├── server.py       # Main server implementation
│   │   └── test.py         # Test scripts
│   │
│   ├── doc-index/           # Document indexing and querying service
│   │   ├── Dockerfile      # Container configuration
│   │   ├── requirements.txt# Dependencies
│   │   ├── server.py       # Main server implementation
│   │   └── test.py         # Test scripts
│   │
│   ├── base-sdk/            # Base SDK implementation
│   │   ├── Dockerfile      # Container configuration
│   │   ├── requirements.txt# Dependencies
│   │   ├── server.py       # Main server implementation
│   │   └── tools.py        # Core SDK tools
│   │
│   └── docker-compose.yml  # Local development configuration
```

## 🚀 Available Servers

### Audio Index Server
Located in `servers/audio-index/`, this server provides:
- Audio file indexing with transcription capabilities
- Semantic search over audio content
- Multi-index support for audio collections
- Accessible via ALB at `/audio`

### Video Index Server
Located in `servers/video-index/`, this server provides:
- Video file indexing with frame extraction
- Content-based video search
- Accessible via ALB at `/video`

### Image Index Server
Located in `servers/image-index/`, this server provides:
- Image indexing with object detection
- Similarity search for images
- Accessible via ALB at `/image`

### Document Index Server
Located in `servers/doc-index/`, this server provides:
- Document indexing with text extraction
- Retrieval-Augmented Generation (RAG) support
- Accessible via ALB at `/doc`

### Base SDK Server
Located in `servers/base-sdk/`, this server provides:
- Core functionality for Pixeltable integration
- Foundation for building specialized servers

## 📦 Installation

### Local Development
```bash
pip install pixeltable
git clone https://github.com/yourusername/mcp-server-pixeltable.git
cd mcp-server-pixeltable
pip install -r servers/*/requirements.txt  # Install dependencies for each service
docker-compose up --build                 # Run locally with docker-compose
```

### AWS Deployment
1. Install AWS CDK:
   ```bash
   npm install -g aws-cdk
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Bootstrap CDK (first time only):
   ```bash
   cdk bootstrap
   ```
4. Deploy to AWS ECS:
   ```bash
   cdk deploy
   ```

## 🌐 Accessing Services
After deployment, the AWS CDK will output the ALB DNS name. Access the services at:
- `http://<alb-dns>/audio` for Audio Index
- `http://<alb-dns>/video` for Video Index
- `http://<alb-dns>/image` for Image Index
- `http://<alb-dns>/doc` for Document Index

## 🔧 Configuration
- Each service runs on its designated port (8080 for audio, 8081 for video, 8082 for image, 8083 for doc).
- Auto-scaling is enabled with 1-4 tasks per service, targeting 70% CPU utilization.
- Resources per task: 0.5 vCPU and 1 GiB memory.

## 🔗 Links
- [Pixeltable GitHub](https://github.com/pixeltable/pixeltable)
- [Pixeltable Documentation](https://docs.pixeltable.io)
- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/v2/guide/home.html)
- [Discord Community](https://discord.gg/pixeltable)

## 📞 Support
- GitHub Issues: [Report bugs or request features](https://github.com/yourusername/mcp-server-pixeltable/issues)
- Discord: Join our [community](https://discord.gg/pixeltable)

## 📜 License
This project is licensed under the Apache 2.0 License.