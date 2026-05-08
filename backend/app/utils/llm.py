# app/utils/llm.py

"""
PHASE 2 — ENTERPRISE LLM ORCHESTRATION

Capabilities:
1. Ollama integration
2. Retry handling
3. Timeout control
4. Production-safe validation
5. Strict response validation
6. Failure resilience
7. Enterprise logging support

Model:
mistral

Future upgrade ready for:
- Azure OpenAI
- AWS Bedrock
- Claude
- GPT Enterprise
"""

import time
import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "mistral"

REQUEST_TIMEOUT = 600
MAX_RETRIES = 3
RETRY_WAIT_SECONDS = 2


# =====================================================
# VALIDATE RESPONSE
# =====================================================

def validate_response(data):
    """
    Ensure Ollama returned valid structure.
    """

    if not isinstance(data, dict):
        raise Exception(
            "Invalid response format from Ollama"
        )

    if "response" not in data:
        raise Exception(
            "Missing 'response' field from Ollama"
        )

    if not data["response"]:
        raise Exception(
            "Empty response returned from Ollama"
        )

    return data["response"]


# =====================================================
# CALL LLM
# =====================================================

def call_llm(prompt):
    """
    Enterprise-safe LLM execution.

    Features:
    - retries
    - timeout handling
    - structured validation
    - detailed logging
    - failure-safe exceptions
    """

    print("\n================================")
    print("LLM REQUEST STARTED")
    print("================================")

    for attempt in range(
        1,
        MAX_RETRIES + 1
    ):
        try:
            print(
                f"Attempt {attempt}/{MAX_RETRIES}"
            )

            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=REQUEST_TIMEOUT
            )

            print(
                f"Ollama Status Code: "
                f"{response.status_code}"
            )

            print(
                "Raw Ollama Response:"
            )
            print(response.text[:2000])

            response.raise_for_status()

            data = response.json()

            validated_output = validate_response(
                data
            )

            print(
                "LLM request completed successfully"
            )

            return validated_output

        except requests.Timeout:
            print(
                f"Timeout on attempt {attempt}"
            )

            if attempt == MAX_RETRIES:
                raise Exception(
                    "LLM timeout after multiple retries"
                )

        except requests.ConnectionError:
            print(
                f"Connection error on attempt {attempt}"
            )

            if attempt == MAX_RETRIES:
                raise Exception(
                    "Cannot connect to Ollama. "
                    "Ensure Ollama is running."
                )

        except requests.HTTPError as e:
            print(
                f"HTTP error on attempt {attempt}: "
                f"{str(e)}"
            )

            if attempt == MAX_RETRIES:
                raise Exception(
                    f"Ollama HTTP failure: {str(e)}"
                )

        except Exception as e:
            print(
                f"Unexpected LLM error: {str(e)}"
            )

            if attempt == MAX_RETRIES:
                raise Exception(
                    f"Ollama failed: {str(e)}"
                )

        time.sleep(
            RETRY_WAIT_SECONDS
        )

    raise Exception(
        "LLM request failed unexpectedly"
    )