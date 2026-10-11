"""Unit tests for the Disposal Rules Engine and Safety Guardrails."""

import pytest
from backend.rules_engine import (
    DisposalRulesEngine,
    WasteAnalysisInput,
    UNCERTAINTY_CONFIDENCE_THRESHOLD,
)


@pytest.fixture
def engine():
    return DisposalRulesEngine()


def test_recyclable_aluminum_can(engine):
    """Clean aluminum can should be classified as recyclable with high confidence."""
    analysis = WasteAnalysisInput(
        item_name="Aluminum Soda Can",
        material="Aluminum metal",
        detected_category="recyclable",
        confidence=0.95,
        condition="clean",
        hazard_tags=[],
        is_uncertain=False,
    )
    result = engine.evaluate(analysis)
    assert result.category == "recyclable"
    assert result.is_uncertain is False
    assert result.confidence_level == "high"
    assert any("rinse" in step.lower() or "empty" in step.lower() for step in result.disposal_instructions)
    assert len(result.safety_warnings) == 0


def test_organic_banana_peel(engine):
    """Fruit scraps should be classified as organic with produce sticker prep step."""
    analysis = WasteAnalysisInput(
        item_name="Banana Peel",
        material="Organic fruit peel",
        detected_category="organic",
        confidence=0.96,
        condition="normal",
        hazard_tags=[],
        is_uncertain=False,
    )
    result = engine.evaluate(analysis)
    assert result.category == "organic"
    assert result.is_uncertain is False
    assert any("sticker" in prep.lower() for prep in result.preparation_steps)
    assert any("compost" in inst.lower() for inst in result.disposal_instructions)


def test_hazardous_battery_override(engine):
    """Batteries must always trigger hazardous category and safety warnings."""
    analysis = WasteAnalysisInput(
        item_name="Lithium-Ion Phone Battery",
        material="Lithium cobalt oxide",
        detected_category="hazardous",
        confidence=0.92,
        condition="battery_included",
        hazard_tags=["flammable", "fire_hazard"],
        is_uncertain=False,
    )
    result = engine.evaluate(analysis)
    assert result.category == "hazardous"
    assert result.is_uncertain is False
    assert any("tape" in step.lower() for step in result.disposal_instructions)
    assert any("fire" in warn.lower() for warn in result.safety_warnings)


def test_hazardous_override_beats_clean_recyclable_claim(engine):
    """Even if an AI erroneously detects a battery as recyclable, safety rule forces hazardous."""
    analysis = WasteAnalysisInput(
        item_name="Rechargeable AA Battery",
        material="Nickel metal hydride",
        detected_category="recyclable",  # Erroneous AI classification
        confidence=0.88,
        condition="clean",
        hazard_tags=["fire_hazard"],
        is_uncertain=False,
    )
    result = engine.evaluate(analysis)
    assert result.category == "hazardous", "Rules engine MUST override recyclable to hazardous for batteries"
    assert any("terminal" in prep.lower() or "tape" in prep.lower() for prep in result.preparation_steps)


def test_greasy_pizza_box_contamination_guard(engine):
    """Greasy pizza box must warn against contaminating paper recycling."""
    analysis = WasteAnalysisInput(
        item_name="Greasy Pizza Box",
        material="Corrugated cardboard",
        detected_category="general",
        confidence=0.85,
        condition="greasy",
        hazard_tags=[],
        is_uncertain=False,
    )
    result = engine.evaluate(analysis)
    assert any("grease" in warn.lower() or "fiber" in warn.lower() for warn in result.safety_warnings)
    assert any("tear" in inst.lower() or "lid" in inst.lower() for inst in result.disposal_instructions)


def test_uncertain_low_confidence_triggers_safety_fallback(engine):
    """Low confidence (< 0.65) must trigger uncertainty guard and never go to recyclable."""
    analysis = WasteAnalysisInput(
        item_name="Unidentified Metallic-Looking Cylinder",
        material="Unknown metal or plastic",
        detected_category="recyclable",
        confidence=0.45,  # Below threshold
        condition="normal",
        hazard_tags=[],
        is_uncertain=False,
    )
    result = engine.evaluate(analysis)
    assert result.is_uncertain is True
    assert result.category != "recyclable", "Uncertain items must never enter recyclable stream"
    assert result.confidence_level == "low"
    assert any("uncertain" in warn.lower() or "wishcycling" in warn.lower() for warn in result.safety_warnings)


def test_uncertain_with_potential_hazard_defaults_to_hazardous(engine):
    """An uncertain item with hazard keywords must default to hazardous precautionary protocol."""
    analysis = WasteAnalysisInput(
        item_name="Unknown chemical solvent bottle",
        material="Unknown liquid in plastic",
        detected_category="general",
        confidence=0.50,
        condition="unknown",
        hazard_tags=["toxic"],
        is_uncertain=True,
    )
    result = engine.evaluate(analysis)
    assert result.is_uncertain is True
    assert result.category == "hazardous"
    assert any("household hazardous waste" in inst.lower() for inst in result.disposal_instructions)


def test_styrofoam_diverted_from_recycling(engine):
    """Expanded polystyrene (Styrofoam) must not be marked recyclable."""
    analysis = WasteAnalysisInput(
        item_name="Styrofoam Takeout Box",
        material="Expanded Polystyrene #6",
        detected_category="recyclable",  # Erroneous category
        confidence=0.85,
        condition="clean",
        hazard_tags=[],
        is_uncertain=False,
        raw_query="styrofoam cup",
    )
    result = engine.evaluate(analysis)
    assert result.category == "general"
    assert any("curbside" in warn.lower() or "styrofoam" in warn.lower() for warn in result.safety_warnings)
