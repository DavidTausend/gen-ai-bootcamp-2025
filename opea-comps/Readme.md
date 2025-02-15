## Running Ollama Thrid-Party Service

This guide provides a step-by-step approach to installing and running Ollama on a macOS system.

### Software requierements
- macOS
- Homebrew
- Docker

### Docker installation on Mac

To install docker on the Mac, first we must a Homebrew, the most populer package manager for macOS.

Install Homebrew:
```sh
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Once Homebrew is installed, continue wiht docker:
```sh
brew install --cask docker
```

Strart or open the docker application:
```sh
open /Applications/Docker.app
```
Check the version:
```sh
docker --version
```

https://www.youtube.com/watch?v=-EXlfSsP49A
https://forums.docker.com/t/docker-command-not-found-after-installing-docker-desktop-on-mac/93837?utm_source=chatgpt.com

### Choosing a Model

You can get the model_id that ollama will launch from the [Ollama Library](https://ollama.com/library).

https://ollama.com/library/llama3.2

eg. LLM_MODEL_ID="llama3.2:1b"

### Getting the Host IP

#### Mac

Get your IP address by choosing your network card en0
```sh
ifconfig
```

### Download (Pull) a model

Add the localhost port which the container is running, that might be 8008

curl http://localhost:8008/api/pull -d '{
  "model": "llama3.2:1b"
}'

### Generate a Request

curl http://localhost:8008/api/generate -d '{
  "model": "llama3.2:1b",
  "prompt": "Why is the sky blue?"
}'

### Ollama API

Once the Ollama server is running we can make API calls to the ollama API

https://github.com/ollama/ollama/blob/main/docs/api.md
