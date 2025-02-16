import os
import json
import logging
from fastapi import HTTPException
from comps import MicroService, ServiceOrchestrator
from comps.cores.mega.constants import ServiceType, ServiceRoleType
from comps.cores.proto.api_protocol import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionResponseChoice,
    ChatMessage,
    UsageInfo
)
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

# Configure OpenTelemetry
OTEL_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")
provider = TracerProvider()
processor = SimpleSpanProcessor(OTLPSpanExporter(endpoint=f"{OTEL_ENDPOINT}/v1/traces"))
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

# Environment Variables
EMBEDDING_SERVICE_HOST_IP = os.getenv("EMBEDDING_SERVICE_HOST_IP", "0.0.0.0")
EMBEDDING_SERVICE_PORT = os.getenv("EMBEDDING_SERVICE_PORT", 6000)
LLM_SERVICE_HOST_IP = os.getenv("LLM_SERVICE_HOST_IP", "0.0.0.0")
LLM_SERVICE_PORT = os.getenv("LLM_SERVICE_PORT", 8008)

# Enable logging
logging.basicConfig(level=logging.DEBUG)

class ExampleService:
    def __init__(self, host="0.0.0.0", port=8000):
        print("hello")
        os.environ["TELEMETRY_ENDPOINT"] = ""
        self.host = host
        self.port = port
        self.endpoint = "/v1/example-service"
        self.megaservice = ServiceOrchestrator()
    
    def add_remote_service(self):
        llm = MicroService(
            name="llm",
            host=LLM_SERVICE_HOST_IP,
            port=LLM_SERVICE_PORT,
            endpoint="/v1/chat/completions",
            use_remote_service=True,
            service_type=ServiceType.LLM,
        )
        self.megaservice.add(llm)
    
    def start(self):
        self.service = MicroService(
            self.__class__.__name__,
            service_role=ServiceRoleType.MEGASERVICE,
            host=self.host,
            port=self.port,
            endpoint=self.endpoint,
            input_datatype=ChatCompletionRequest,
            output_datatype=ChatCompletionResponse,
        )
        self.service.add_route(self.endpoint, self.handle_request, methods=["POST"])
        self.service.start()
    
    async def handle_request(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        with tracer.start_as_current_span("handle_request"):
            try:
                # Ensure correct format for "messages"
                formatted_messages = [{"role": "user", "content": request.messages}]
                
                ollama_request = {
                    "model": request.model or "llama3.2:1b",
                    "messages": request.messages,
                    "stream": False
                }
                
                logging.debug(f"Sending request to Ollama: {json.dumps(ollama_request, indent=2)}")
                
                result = await self.megaservice.schedule(ollama_request)
                
                logging.debug(f"Ollama Response: {result}")
                
                if isinstance(result, tuple) and len(result) > 0:
                    llm_response = result[0].get("llm/MicroService")
                    
                    if hasattr(llm_response, "body"):
                        response_body = b""
                        async for chunk in llm_response.body_iterator:
                            response_body += chunk
                        content = response_body.decode("utf-8")
                    else:
                        content = "No response content available"
                else:
                    content = "Invalid response format"
                
                response = ChatCompletionResponse(
                    model=request.model or "example-model",
                    choices=[
                        ChatCompletionResponseChoice(
                            index=0,
                            message=ChatMessage(
                                role="assistant",
                                content=content
                            ),
                            finish_reason="stop"
                        )
                    ],
                    usage=UsageInfo(
                        prompt_tokens=0,
                        completion_tokens=0,
                        total_tokens=0
                    )
                )
                
                return response
            
            except Exception as e:
                logging.error(f"Error handling request: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))

# Initialize and start the service
example = ExampleService()
example.add_remote_service()
example.start()
