FROM python:3.11-slim

# Create a user for security purposes
RUN useradd -m -s /bin/bash user && \
    mkdir -p /home/user && \
    chown -R user /home/user/

# Set environment variables
ENV LANG=C.UTF-8
ARG ARCH=cpu

# Set working directory
WORKDIR /home/user/tts

# Copy the entire tts/src directory into the container
COPY ./tts/src /home/user/tts/src

# Upgrade pip and install dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools && \
    if [ "${ARCH}" = "cpu" ]; then \
    pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu ; \
    fi && \
    pip install --no-cache-dir -r /home/user/tts/src/requirements.txt

# Switch to the created user
USER user

# Set the working directory for execution
WORKDIR /home/user/tts/src

# Expose API port
EXPOSE 8000

# Run the TTS service
ENTRYPOINT ["python", "opea_tts_microservice.py"]
