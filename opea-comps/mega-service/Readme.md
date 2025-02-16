# Run OpenTelemetry Collector

```sh
docker run --rm -p 4318:4318 otel/opentelemetry-collector
```

# Request

```sh
curl -X POST http://localhost:8008/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.2:1b",
    "messages": [
      {
        "role": "user",
        "content": "Hello, how are you?"
      }
    ],
    "stream": false
  }'
```

```sh
  curl -X POST http://localhost:8000/v1/example-service \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "Hello, this is a test message"
      }
    ],
    "model": "test-model",
    "max_tokens": 100,
    "temperature": 0.7
  }'
```

# Resolution of 400 Bad Request Error in Ollama Integration

There was a 400 bad resquest error when the application attempted to communicate with the Ollama server's /v1/chat/completions endpoint.This error indicates that the server could not process the request due to malformed syntax or invalid data.

## Root cause

The primary issue was the incorrect formatting of the messages field in the request payload. Your application was sending the messages as a list containing a dictionary with a content key that itself held a list of message dictionaries:

```sh
{
  "model": "llama3.2:1b",
  "messages": "Hello, how are you?"
}
```

This nesting does not align with the expected structure defined by the Ollama API.

## Solution

The messages field should be formatted as a list of dictionaries, where each dictionary represents a message with role and content keys. The corrected structure is:

```sh
"messages": [
  {
    "role": "user",
    "content": "Hello, how are you?"
  }
]
```

This adjustment ensures that the payload conforms to the API's expected format, allowing the server to process the request correctly.

## References

- Ollama API Documentation: https://github.com/ollama/ollama/blob/main/docs/api.md
- Discussion on 400 Bad Request Errors: https://www.reddit.com/r/ollama/comments/1fej2rv/error_code_400/
