"""Unit tests for AI Classifier (Mock and Bedrock interfaces)."""

import pytest
from backend.ai_classifier import MockClassifier, BedrockClassifier, get_classifier


@pytest.fixture
def mock_classifier():
    return MockClassifier()


def test_mock_classifier_known_items(mock_classifier):
    # Recyclable
    res = mock_classifier.classify(text="aluminum soda can")
    assert res.detected_category == "recyclable"
    assert res.confidence >= 0.85
    assert res.is_uncertain is False

    # Organic
    res = mock_classifier.classify(text="banana peel")
    assert res.detected_category == "organic"
    assert res.confidence >= 0.85

    # Hazardous
    res = mock_classifier.classify(text="lithium-ion battery")
    assert res.detected_category == "hazardous"
    assert "flammable" in res.hazard_tags or "fire_hazard" in res.hazard_tags

    # General
    res = mock_classifier.classify(text="styrofoam coffee cup")
    assert res.detected_category == "general"


def test_mock_classifier_uncertain_and_gibberish(mock_classifier):
    """Gibberish or unknown items must return low confidence and is_uncertain=True."""
    res1 = mock_classifier.classify(text="asdfghjkl12345")
    assert res1.is_uncertain is True
    assert res1.confidence < 0.65

    res2 = mock_classifier.classify(text="???")
    assert res2.is_uncertain is True
    assert res2.confidence < 0.65

    res3 = mock_classifier.classify(text="mysterious strange substance")
    assert res3.is_uncertain is True


def test_mock_classifier_image_only_safe_uncertainty(mock_classifier):
    """Image-only input in mock mode must not invent recognition and must return safe uncertainty."""
    dummy_image = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00"
    res = mock_classifier.classify(image_bytes=dummy_image, image_type="image/jpeg")

    assert res.is_uncertain is True
    assert res.confidence <= 0.50
    assert res.detected_category == "general"
    assert "Image Only" in res.item_name
    assert "[uploaded image]" not in res.item_name.lower()
    assert "mock mode" in res.ai_explanation.lower()


def test_mock_classifier_image_with_text_description(mock_classifier):
    """When an image is accompanied by a text description, mock classifier uses the description."""
    dummy_image = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00"
    res = mock_classifier.classify(text="banana peel", image_bytes=dummy_image, image_type="image/jpeg")

    assert res.detected_category == "organic"
    assert res.confidence >= 0.85
    assert res.is_uncertain is False
    assert "Banana Peel" in res.item_name
    assert "image attached" in res.ai_explanation.lower()


def test_get_classifier_mock_mode():
    clf = get_classifier(force_mock=True)
    assert isinstance(clf, MockClassifier)


def test_bedrock_classifier_graceful_fallback(monkeypatch):
    """Bedrock classifier should gracefully fallback to mock if AWS client throws error."""
    clf = BedrockClassifier(region_name="us-east-1")
    # Invoking with no AWS creds should fallback safely without crashing
    res = clf.classify(text="aluminum can")
    assert res.detected_category == "recyclable"
