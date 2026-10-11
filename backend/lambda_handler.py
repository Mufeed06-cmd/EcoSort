"""AWS Lambda Handler for AI Waste Segregation Advisor.

Handles API Gateway proxy events for `POST /analyze` with CORS support,
payload validation, and orchestration between AI Classifier and Rules Engine.
"""

import json
import base64
import logging
from typing import Dict, Any, Tuple

from .rules_engine import DisposalRulesEngine
from .ai_classifier import get_classifier

logger = logging.getLogger()
logger.setLevel(logging.INFO)

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
    "Access-Control-Allow-Methods": "POST,OPTIONS",
}

# Maximum allowed image size in bytes (5 MB)
MAX_IMAGE_BYTES = 5 * 1024 * 1024


def build_response(status_code: int, body_data: Dict[str, Any]) -> Dict[str, Any]:
    """Format standard API Gateway response."""
    return {
        "statusCode": status_code,
        "headers": {
            **CORS_HEADERS,
            "Content-Type": "application/json",
        },
        "body": json.dumps(body_data),
    }


def parse_and_validate_request(event: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
    """Extract and validate the request body from API Gateway event."""
    # Check HTTP Method
    http_method = event.get("httpMethod") or event.get("requestContext", {}).get("http", {}).get("method")
    if http_method == "OPTIONS":
        return {}, "OPTIONS"

    if http_method and http_method.upper() != "POST":
        raise ValueError(f"Method {http_method} not allowed. Please use POST.")

    body = event.get("body")
    if not body:
        raise ValueError("Request body cannot be empty.")

    if isinstance(body, str):
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON in request body.")
    elif isinstance(body, dict):
        payload = body
    else:
        raise ValueError("Unsupported body payload format.")

    text = payload.get("text", "").strip()
    image_raw = payload.get("image", "").strip()

    if not text and not image_raw:
        raise ValueError("Please provide at least a waste description 'text' or an 'image'.")

    return payload, "POST"


ALLOWED_IMAGE_MIME_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
    "image/gif",
}


def extract_image_data(image_string: str) -> Tuple[bytes, str]:
    """Parse data URI or raw base64 image string into bytes and mime type."""
    if not image_string or not isinstance(image_string, str) or not image_string.strip():
        raise ValueError("Image data cannot be empty.")

    clean_base64 = image_string.strip()
    mime_type = "image/jpeg"

    if "base64," in clean_base64:
        header, clean_base64 = clean_base64.split("base64,", 1)
        clean_base64 = clean_base64.strip()
        if "data:" in header:
            raw_mime = header.split("data:", 1)[1].split(";")[0].strip().lower()
            if raw_mime:
                mime_type = raw_mime

    if mime_type == "image/jpg":
        mime_type = "image/jpeg"

    if mime_type not in ALLOWED_IMAGE_MIME_TYPES:
        raise ValueError(
            f"Unsupported image type '{mime_type}'. Supported formats: JPEG, PNG, WEBP, GIF."
        )

    try:
        image_bytes = base64.b64decode(clean_base64, validate=True)
    except Exception as e:
        raise ValueError(f"Invalid base64 encoding for image: {e}")

    if len(image_bytes) == 0:
        raise ValueError("Uploaded image payload contains 0 bytes.")

    if len(image_bytes) > MAX_IMAGE_BYTES:
        raise ValueError(f"Image exceeds maximum allowable size of {MAX_IMAGE_BYTES / (1024 * 1024):.1f} MB.")

    return image_bytes, mime_type


def analyze_waste(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Main business logic function executing AI classification and Rules Engine."""
    text = payload.get("text", "").strip()
    image_str = payload.get("image", "").strip()
    force_mock = bool(payload.get("mock", False))

    image_bytes = None
    image_type = None

    if image_str:
        image_bytes, image_type = extract_image_data(image_str)

    # 1. AI Identification Step
    classifier = get_classifier(force_mock=force_mock)
    ai_result = classifier.classify(
        text=text if text else None,
        image_bytes=image_bytes,
        image_type=image_type,
        raw_query=text if text else None,
    )

    # 2. Deterministic Disposal & Safety Rules Engine Step
    rules_engine = DisposalRulesEngine()
    source_name = "mock" if (force_mock or classifier.__class__.__name__ == "MockClassifier") else "bedrock"
    final_output = rules_engine.evaluate(ai_result, source=source_name)

    return final_output.to_dict()


def lambda_handler(event: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    """Entry point for AWS Lambda invocations."""
    try:
        # Preflight OPTIONS handling
        payload, method = parse_and_validate_request(event)
        if method == "OPTIONS":
            return build_response(200, {"message": "CORS preflight OK"})

        # Analyze waste item
        result = analyze_waste(payload)
        return build_response(200, result)

    except ValueError as val_err:
        logger.warning(f"Validation error: {val_err}")
        return build_response(400, {
            "status": "error",
            "error_type": "ValidationError",
            "message": str(val_err)
        })

    except Exception as exc:
        logger.exception(f"Internal server error: {exc}")
        return build_response(500, {
            "status": "error",
            "error_type": "InternalServerError",
            "message": "An unexpected error occurred while processing waste analysis. Please try again."
        })
