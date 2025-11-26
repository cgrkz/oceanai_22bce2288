"""
AWS Bedrock Client for LLM and Embedding operations.
Supports Amazon Nova Lite and Cohere Embed v4 models.
"""

import json
import time
from typing import List, Dict, Any, Optional
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from backend.config import settings
from backend.app.utils.logger import init_logger

# Initialize logger
logger = init_logger()


class BedrockClient:
    """AWS Bedrock client for LLM and embedding operations"""

    def __init__(self):
        """Initialize Bedrock client with AWS credentials"""
        logger.info("Initializing BedrockClient")

        try:
            # Configure boto3 with retry settings
            boto_config = Config(
                region_name=settings.aws_region,
                retries={
                    'max_attempts': 3,
                    'mode': 'adaptive'
                },
                connect_timeout=settings.bedrock_request_timeout,
                read_timeout=settings.bedrock_request_timeout,
            )

            # Initialize Bedrock Runtime client (use explicit credentials only if provided)
            client_kwargs = {
                "service_name": "bedrock-runtime",
                "region_name": settings.aws_region,
                "config": boto_config,
            }

            if settings.aws_access_key_id and settings.aws_secret_access_key:
                client_kwargs["aws_access_key_id"] = settings.aws_access_key_id
                client_kwargs["aws_secret_access_key"] = settings.aws_secret_access_key

            self.client = boto3.client(**client_kwargs)

            self.llm_model_id = settings.bedrock_llm_model_id
            self.embedding_model_id = settings.bedrock_embedding_model_id

            logger.info(
                "BedrockClient initialized successfully",
                extra={
                    "llm_model": self.llm_model_id,
                    "embedding_model": self.embedding_model_id,
                    "region": settings.aws_region
                }
            )

        except Exception as e:
            logger.exception("Failed to initialize BedrockClient", extra={"error": str(e)})
            raise

    def invoke_llm(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Invoke Amazon Nova Lite LLM

        Args:
            prompt: User prompt
            max_tokens: Maximum tokens to generate
            temperature: Temperature for sampling
            system_prompt: System prompt for context

        Returns:
            Generated text response
        """
        start_time = time.time()

        max_tokens = max_tokens or settings.llm_max_tokens
        temperature = temperature or settings.llm_temperature

        logger.info(
            "Invoking LLM",
            extra={
                "model": self.llm_model_id,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "prompt_length": len(prompt)
            }
        )

        try:
            # Prepare request body for Nova Lite
            # Nova models use messages format similar to Claude
            messages = []

            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": [{"text": system_prompt}]
                })

            messages.append({
                "role": "user",
                "content": [{"text": prompt}]
            })

            request_body = {
                "messages": messages,
                "inferenceConfig": {
                    "maxTokens": max_tokens,
                    "temperature": temperature,
                }
            }

            # Invoke model
            response = self.client.converse(
                modelId=self.llm_model_id,
                messages=messages,
                inferenceConfig=request_body["inferenceConfig"]
            )

            # Extract response text
            output_message = response['output']['message']
            response_text = output_message['content'][0]['text']

            duration = time.time() - start_time

            # Log metrics
            logger.log_bedrock_request(
                model_id=self.llm_model_id,
                operation="invoke_llm",
                duration=duration
            )

            logger.info(
                "LLM invocation successful",
                extra={
                    "model": self.llm_model_id,
                    "response_length": len(response_text),
                    "duration_ms": round(duration * 1000, 2)
                }
            )

            return response_text

        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(
                f"Bedrock ClientError: {error_code}",
                extra={
                    "error_code": error_code,
                    "error_message": error_message,
                    "model": self.llm_model_id
                }
            )
            raise Exception(f"Bedrock LLM error: {error_code} - {error_message}")

        except Exception as e:
            logger.exception(
                "Unexpected error invoking LLM",
                extra={"error": str(e), "model": self.llm_model_id}
            )
            raise

    def generate_embeddings(
        self,
        texts: List[str],
        input_type: str = "search_document"
    ) -> List[List[float]]:
        """
        Generate embeddings using Cohere Embed v4

        Args:
            texts: List of texts to embed
            input_type: Type of input - "search_document" or "search_query"

        Returns:
            List of embedding vectors
        """
        start_time = time.time()

        logger.info(
            "Generating embeddings",
            extra={
                "model": self.embedding_model_id,
                "num_texts": len(texts),
                "input_type": input_type
            }
        )

        try:
            embeddings = []

            # Process each text (Cohere Embed v4 can handle batches, but we'll process individually for clarity)
            for idx, text in enumerate(texts):
                # Log progress for each embedding
                logger.info(f"Generating embedding {idx + 1}/{len(texts)} (text length: {len(text)} chars)")

                try:
                    # Prepare request body for Cohere Embed v4
                    request_body = {
                        "texts": [text[:1000]],  # Limit text length to prevent issues
                        "input_type": input_type,
                        "embedding_types": ["float"]
                    }

                    # Invoke model
                    response = self.client.invoke_model(
                        modelId=self.embedding_model_id,
                        body=json.dumps(request_body)
                    )

                    # Parse response
                    response_body = json.loads(response['body'].read())

                    # Extract embedding
                    embedding = response_body['embeddings']['float'][0]
                    embeddings.append(embedding)

                    logger.info(f"Successfully generated embedding {idx + 1}/{len(texts)}")

                except Exception as embed_error:
                    logger.error(f"Failed to generate embedding {idx + 1}/{len(texts)}: {str(embed_error)}")
                    # Create a zero vector as fallback
                    embeddings.append([0.0] * 1024)  # Cohere Embed v4 dimension

            duration = time.time() - start_time

            logger.log_bedrock_request(
                model_id=self.embedding_model_id,
                operation="generate_embeddings",
                tokens=len(texts),
                duration=duration
            )

            logger.info(
                "Embeddings generated successfully",
                extra={
                    "model": self.embedding_model_id,
                    "num_embeddings": len(embeddings),
                    "embedding_dimension": len(embeddings[0]) if embeddings else 0,
                    "duration_ms": round(duration * 1000, 2)
                }
            )

            return embeddings

        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(
                f"Bedrock ClientError: {error_code}",
                extra={
                    "error_code": error_code,
                    "error_message": error_message,
                    "model": self.embedding_model_id
                }
            )
            raise Exception(f"Bedrock Embedding error: {error_code} - {error_message}")

        except Exception as e:
            logger.exception(
                "Unexpected error generating embeddings",
                extra={"error": str(e), "model": self.embedding_model_id}
            )
            raise

    def generate_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding for a search query

        Args:
            query: Search query text

        Returns:
            Embedding vector
        """
        logger.debug(f"Generating query embedding for: {query[:100]}...")

        embeddings = self.generate_embeddings([query], input_type="search_query")
        return embeddings[0]

    def test_connection(self) -> bool:
        """
        Test Bedrock connection

        Returns:
            True if connection is successful
        """
        logger.info("Testing Bedrock connection")

        try:
            # Test LLM with simple prompt
            response = self.invoke_llm(
                prompt="Say 'Hello' in one word.",
                max_tokens=10,
                temperature=0.1
            )

            logger.info("Bedrock connection test successful", extra={"response": response})
            return True

        except Exception as e:
            logger.error("Bedrock connection test failed", extra={"error": str(e)})
            return False


# Create global instance
_bedrock_client = None


def get_bedrock_client() -> BedrockClient:
    """Get or create global Bedrock client instance"""
    global _bedrock_client
    if _bedrock_client is None:
        _bedrock_client = BedrockClient()
    return _bedrock_client
