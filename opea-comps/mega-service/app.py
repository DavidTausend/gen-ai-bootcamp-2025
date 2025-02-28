import os
import json
import logging
import aiohttp
from fastapi import HTTPException, Request
from fastapi.responses import StreamingResponse
from comps import MicroService, ServiceOrchestrator
from comps.cores.mega.constants import ServiceType, ServiceRoleType
from comps.cores.proto.api_protocol import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionResponseChoice,
    ChatMessage,
    UsageInfo
)
from comps.cores.proto.docarray import LLMParams
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
        print("Initializing ExampleService...")
        self.host = host
        self.port = port
        self.endpoint = "/v1/example-service"
        self.megaservice = ServiceOrchestrator()
        os.environ["LOGFLAG"] = "true"  # Enable detailed logging

    async def check_ollama_connection(self):
        """Check if we can connect to Ollama"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"http://{LLM_SERVICE_HOST_IP}:{LLM_SERVICE_PORT}/api/tags"
                async with session.get(url) as response:
                    logging.debug(f"Ollama check status: {response.status}")
                    return response.status == 200
        except Exception as e:
            logging.error(f"Failed to connect to Ollama: {e}")
            return False

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
        logging.debug(f"Configured LLM service: {LLM_SERVICE_HOST_IP}:{LLM_SERVICE_PORT}")

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

    async def handle_request(self, request: Request):
        with tracer.start_as_current_span("handle_request"):
            try:
                if not await self.check_ollama_connection():
                    raise HTTPException(status_code=500, detail="Cannot connect to Ollama service")

                data = await request.json()
                logging.debug(f"Received request data: {json.dumps(data, indent=2)}")

                chat_request = ChatCompletionRequest.model_validate(data)
                stream_opt = data.get("stream", True)

                parameters = LLMParams(
                    max_tokens=chat_request.max_tokens or 1024,
                    top_k=chat_request.top_k or 10,
                    top_p=chat_request.top_p or 0.95,
                    temperature=chat_request.temperature or 0.01,
                    frequency_penalty=chat_request.frequency_penalty or 0.0,
                    presence_penalty=chat_request.presence_penalty or 0.0,
                    repetition_penalty=chat_request.repetition_penalty or 1.03,
                    stream=stream_opt,
                    model=chat_request.model,
                    chat_template=chat_request.chat_template or None,
                )

                initial_inputs = {"messages": chat_request.messages}
                logging.debug(f"LLM request payload: {json.dumps(initial_inputs, indent=2)}")

                result_dict, runtime_graph = await self.megaservice.schedule(
                    initial_inputs=initial_inputs, llm_parameters=parameters
                )

                for node, response in result_dict.items():
                    if isinstance(response, StreamingResponse):
                        logging.debug("Streaming response detected, returning stream.")
                        return response

                last_node = runtime_graph.all_leaves()[-1]
                service_result = result_dict.get(last_node, "No response received")

                if isinstance(service_result, dict) and 'choices' in service_result:
                    content = service_result['choices'][0].get('message', {}).get('content', '')
                else:
                    content = str(service_result)

                response = ChatCompletionResponse(
                    model=chat_request.model or "example-model",
                    choices=[
                        ChatCompletionResponseChoice(
                            index=0,
                            message=ChatMessage(role="assistant", content=content),
                            finish_reason="stop",
                        )
                    ],
                    usage=UsageInfo(prompt_tokens=0, completion_tokens=0, total_tokens=0),
                )
                return response

            except Exception as e:
                logging.error(f"Error handling request: {e}")
                raise HTTPException(status_code=500, detail=str(e))

# Initialize and start the service
example = ExampleService()
example.add_remote_service()
example.start()
