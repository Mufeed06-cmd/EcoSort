"""Unit and integration tests for AWS Lambda handler and API Gateway contracts."""

import json
import base64
import pytest
from backend.lambda_handler import lambda_handler, MAX_IMAGE_BYTES


def test_lambda_options_cors_preflight():
    """OPTIONS request must return 200 with CORS headers."""
    event = {
        "httpMethod": "OPTIONS",
        "path": "/analyze",
    }
    response = lambda_handler(event, None)
    assert response["statusCode"] == 200
    assert response["headers"]["Access-Control-Allow-Origin"] == "*"
    assert "POST" in response["headers"]["Access-Control-Allow-Methods"]


def test_lambda_post_valid_text():
    """POST /analyze with text description should return 200 and valid schema."""
    event = {
        "httpMethod": "POST",
        "path": "/analyze",
        "body": json.dumps({"text": "clean aluminum soda can", "mock": True}),
    }
    response = lambda_handler(event, None)
    assert response["statusCode"] == 200
    assert response["headers"]["Content-Type"] == "application/json"

    body = json.loads(response["body"])
    assert body["status"] == "success"
    assert body["category"] == "recyclable"
    assert body["is_uncertain"] is False
    assert isinstance(body["disposal_instructions"], list)
    assert len(body["disposal_instructions"]) > 0
    assert "confidence" in body
    assert body["confidence"] > 0.8
    assert body["source"] == "mock"


def test_lambda_post_image_only_mock_mode_safe_uncertainty():
    """POST /analyze with image-only in mock mode must not invent certainty and must not leak internal string."""
    tiny_jpeg_b64 = "data:image/jpeg;base64," + base64.b64encode(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00").decode("utf-8")
    event = {
        "httpMethod": "POST",
        "path": "/analyze",
        "body": json.dumps({"image": tiny_jpeg_b64, "mock": True}),
    }
    response = lambda_handler(event, None)
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["status"] == "success"
    assert body["is_uncertain"] is True
    assert body["confidence"] <= 0.50
    assert body["category"] == "general"  # Safe default to prevent recycling contamination
    assert "[uploaded image]" not in body["item_name"].lower()
    assert "Image Only" in body["item_name"]
    assert "mock" in body["source"]


def test_lambda_post_image_with_text_mock_mode():
    """POST /analyze with image AND text in mock mode classifies using the text while acknowledging image."""
    tiny_jpeg_b64 = "data:image/jpeg;base64," + base64.b64encode(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00").decode("utf-8")
    event = {
        "httpMethod": "POST",
        "path": "/analyze",
        "body": json.dumps({"text": "banana peel", "image": tiny_jpeg_b64, "mock": True}),
    }
    response = lambda_handler(event, None)
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["status"] == "success"
    assert body["category"] == "organic"
    assert body["confidence"] >= 0.85
    assert body["is_uncertain"] is False
    assert "Banana Peel" in body["item_name"]


def test_lambda_post_valid_png_and_raw_base64():
    """POST /analyze with raw base64 string without data URI scheme."""
    raw_b64 = base64.b64encode(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR").decode("utf-8")
    event = {
        "httpMethod": "POST",
        "path": "/analyze",
        "body": json.dumps({"image": raw_b64, "mock": True}),
    }
    response = lambda_handler(event, None)
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["status"] == "success"
    assert body["is_uncertain"] is True


def test_lambda_post_empty_body():
    """Empty body should return 400 Bad Request."""
    event = {
        "httpMethod": "POST",
        "path": "/analyze",
        "body": json.dumps({}),
    }
    response = lambda_handler(event, None)
    assert response["statusCode"] == 400
    body = json.loads(response["body"])
    assert body["status"] == "error"
    assert "at least a waste description" in body["message"]


def test_lambda_post_invalid_json():
    """Malformed JSON string should return 400 Bad Request."""
    event = {
        "httpMethod": "POST",
        "path": "/analyze",
        "body": "{invalid-json",
    }
    response = lambda_handler(event, None)
    assert response["statusCode"] == 400
    body = json.loads(response["body"])
    assert body["status"] == "error"


def test_lambda_post_zero_byte_image():
    """Image payload with zero bytes should return 400 Bad Request."""
    event = {
        "httpMethod": "POST",
        "path": "/analyze",
        "body": json.dumps({"image": "data:image/jpeg;base64,"}),
    }
    response = lambda_handler(event, None)
    assert response["statusCode"] == 400
    body = json.loads(response["body"])
    assert "0 bytes" in body["message"] or "empty" in body["message"].lower()


def test_lambda_post_corrupt_base64():
    """Malformed base64 characters should return 400 Bad Request."""
    event = {
        "httpMethod": "POST",
        "path": "/analyze",
        "body": json.dumps({"image": "data:image/jpeg;base64,??not_base64??"}),
    }
    response = lambda_handler(event, None)
    assert response["statusCode"] == 400
    body = json.loads(response["body"])
    assert "base64" in body["message"].lower()


def test_lambda_post_unsupported_image_mime():
    """Non-image MIME type (e.g. application/pdf) should return 400 Bad Request."""
    dummy_pdf_b64 = "data:application/pdf;base64," + base64.b64encode(b"%PDF-1.4").decode("utf-8")
    event = {
        "httpMethod": "POST",
        "path": "/analyze",
        "body": json.dumps({"image": dummy_pdf_b64}),
    }
    response = lambda_handler(event, None)
    assert response["statusCode"] == 400
    body = json.loads(response["body"])
    assert "Unsupported image type" in body["message"]


def test_lambda_post_oversized_image():
    """Image payload exceeding 5MB limit should return 400 Bad Request."""
    oversized_bytes = b"x" * (MAX_IMAGE_BYTES + 1024)
    oversized_b64 = "data:image/jpeg;base64," + base64.b64encode(oversized_bytes).decode("utf-8")
    event = {
        "httpMethod": "POST",
        "path": "/analyze",
        "body": json.dumps({"image": oversized_b64}),
    }
    response = lambda_handler(event, None)
    assert response["statusCode"] == 400
    body = json.loads(response["body"])
    assert "exceeds maximum allowable size" in body["message"]


def test_lambda_post_hazardous_lithium_battery():
    """Hazardous items must contain safety warnings in Lambda response."""
    event = {
        "httpMethod": "POST",
        "path": "/analyze",
        "body": json.dumps({"text": "old smartphone lithium battery", "mock": True}),
    }
    response = lambda_handler(event, None)
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["category"] == "hazardous"
    assert len(body["safety_warnings"]) > 0
    assert any("fire" in w.lower() for w in body["safety_warnings"])


def test_lambda_post_uncertain_input():
    """Uncertain input should return is_uncertain=True without inflating confidence."""
    event = {
        "httpMethod": "POST",
        "path": "/analyze",
        "body": json.dumps({"text": "unidentified slimy gray clump", "mock": True}),
    }
    response = lambda_handler(event, None)
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["is_uncertain"] is True
    assert body["confidence"] < 0.65
    assert body["category"] in ["general", "hazardous"]  # Safe default categories
