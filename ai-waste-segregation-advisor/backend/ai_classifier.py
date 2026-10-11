"""AI Classifier module for waste segregation.

Integrates with Amazon Bedrock (multimodal text + image classification)
and provides an intelligent MockClassifier for testing and offline environments.
"""

import os
import json
import base64
import logging
import re
from typing import Optional, Dict, Any

from .rules_engine import WasteAnalysisInput

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Default Bedrock Model ID
DEFAULT_BEDROCK_MODEL = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")
DEFAULT_AWS_REGION = os.getenv("AWS_REGION", "us-east-1")


class BaseClassifier:
    """Base interface for waste classification."""
    def classify(
        self,
        text: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
        image_type: Optional[str] = None,
        raw_query: Optional[str] = None,
    ) -> WasteAnalysisInput:
        raise NotImplementedError


class MockClassifier(BaseClassifier):
    """Deterministic, high-fidelity mock classifier for local development, hackathon demos, and unit testing."""

    # Curated waste taxonomy
    DATABASE = [
        # HAZARDOUS
        {
            "triggers": ["lithium", "battery", "batteries", "aa battery", "aaa battery", "phone battery", "laptop battery"],
            "item_name": "Lithium-Ion / Dry-Cell Battery",
            "material": "Heavy metals, lithium, alkaline electrolyte",
            "detected_category": "hazardous",
            "confidence": 0.95,
            "condition": "battery_included",
            "hazard_tags": ["flammable", "corrosive", "fire_hazard"],
            "is_uncertain": False,
            "ai_explanation": "Identified as a portable chemical battery containing hazardous and reactive heavy metals."
        },
        {
            "triggers": ["motor oil", "engine oil", "car oil", "used oil"],
            "item_name": "Used Motor Oil Container",
            "material": "Petroleum hydrocarbons, chemical additives",
            "detected_category": "hazardous",
            "confidence": 0.96,
            "condition": "soiled",
            "hazard_tags": ["toxic", "environmental_pollutant", "flammable"],
            "is_uncertain": False,
            "ai_explanation": "Petroleum-based automotive lubricant is toxic and prohibited in regular trash or water drainage."
        },
        {
            "triggers": ["cfl", "fluorescent", "mercury bulb", "light bulb", "fluorescent tube"],
            "item_name": "Fluorescent Light Bulb / CFL",
            "material": "Glass, phosphor powder, mercury vapor",
            "detected_category": "hazardous",
            "confidence": 0.92,
            "condition": "fragile",
            "hazard_tags": ["mercury_hazard", "toxic_vapor", "fragile"],
            "is_uncertain": False,
            "ai_explanation": "Contains trace mercury vapor which requires regulated hazardous recovery."
        },
        {
            "triggers": ["pesticide", "insecticide", "weed killer", "herbicide"],
            "item_name": "Pesticide Chemical Container",
            "material": "Agricultural toxic chemicals, plastic jug",
            "detected_category": "hazardous",
            "confidence": 0.94,
            "condition": "chemical_residue",
            "hazard_tags": ["toxic", "chemical_burn", "poison"],
            "is_uncertain": False,
            "ai_explanation": "High-potency pesticide residue creates acute poisoning hazard if mixed into general streams."
        },
        {
            "triggers": ["paint", "varnish", "oil paint", "paint can"],
            "item_name": "Paint Can with Residue",
            "material": "Solvent / latex / heavy metal pigments, steel can",
            "detected_category": "hazardous",
            "confidence": 0.91,
            "condition": "soiled",
            "hazard_tags": ["flammable", "toxic_fumes"],
            "is_uncertain": False,
            "ai_explanation": "Liquid paint and solvent residues contain volatile organic compounds (VOCs)."
        },
        {
            "triggers": ["syringe", "needle", "lancet", "insulin needle"],
            "item_name": "Used Medical Syringe / Sharps",
            "material": "Plastic barrel, stainless steel needle",
            "detected_category": "hazardous",
            "confidence": 0.98,
            "condition": "biohazard",
            "hazard_tags": ["biohazard", "sharp_hazard", "pathogen"],
            "is_uncertain": False,
            "ai_explanation": "Medical sharp constitutes an infectious biohazard."
        },

        # RECYCLABLE
        {
            "triggers": ["aluminum can", "soda can", "coke can", "beer can", "tin can", "metal can", "beverage can"],
            "item_name": "Aluminum Beverage Can",
            "material": "Aluminum metal (#41 ALU)",
            "detected_category": "recyclable",
            "confidence": 0.96,
            "condition": "clean",
            "hazard_tags": [],
            "is_uncertain": False,
            "ai_explanation": "Clean aluminum beverage container with high recovery value."
        },
        {
            "triggers": ["plastic bottle", "water bottle", "pet bottle", "soda bottle"],
            "item_name": "PET Plastic Beverage Bottle",
            "material": "Polyethylene Terephthalate (#1 PET)",
            "detected_category": "recyclable",
            "confidence": 0.94,
            "condition": "clean",
            "hazard_tags": [],
            "is_uncertain": False,
            "ai_explanation": "Rigid PET beverage bottle accepted in standard municipal recycling programs."
        },
        {
            "triggers": ["milk jug", "detergent bottle", "hdpe"],
            "item_name": "HDPE Plastic Jug",
            "material": "High-Density Polyethylene (#2 HDPE)",
            "detected_category": "recyclable",
            "confidence": 0.93,
            "condition": "clean",
            "hazard_tags": [],
            "is_uncertain": False,
            "ai_explanation": "High-density polyethylene container suitable for bottle-to-bottle recycling."
        },
        {
            "triggers": ["cardboard box", "shipping box", "amazon box", "cereal box", "paper box"],
            "item_name": "Corrugated Cardboard Box",
            "material": "Cellulose kraft cardboard",
            "detected_category": "recyclable",
            "confidence": 0.95,
            "condition": "clean",
            "hazard_tags": [],
            "is_uncertain": False,
            "ai_explanation": "Clean dry corrugated cardboard with recyclable wood fibers."
        },
        {
            "triggers": ["glass bottle", "wine bottle", "beer bottle", "glass jar", "jam jar"],
            "item_name": "Glass Bottle / Container Jar",
            "material": "Container soda-lime glass",
            "detected_category": "recyclable",
            "confidence": 0.92,
            "condition": "clean",
            "hazard_tags": [],
            "is_uncertain": False,
            "ai_explanation": "Container glass is 100% recyclable indefinitely when separated from ceramic glass."
        },
        {
            "triggers": ["newspaper", "magazine", "office paper", "printer paper", "envelope"],
            "item_name": "Clean Office Paper / Newspaper",
            "material": "De-inkable paper pulp",
            "detected_category": "recyclable",
            "confidence": 0.91,
            "condition": "clean",
            "hazard_tags": [],
            "is_uncertain": False,
            "ai_explanation": "Dry unlaminated paper pulp is widely recyclable."
        },

        # ORGANIC
        {
            "triggers": ["banana peel", "banana skin", "banana"],
            "item_name": "Banana Peel",
            "material": "Organic fruit peel (potassium-rich cellulose)",
            "detected_category": "organic",
            "confidence": 0.97,
            "condition": "normal",
            "hazard_tags": [],
            "is_uncertain": False,
            "ai_explanation": "Readily biodegradable organic kitchen scrap rich in potassium and nitrogen."
        },
        {
            "triggers": ["apple core", "apple", "fruit scraps", "fruit peel", "orange peel", "lemon peel"],
            "item_name": "Fruit Scraps / Apple Core",
            "material": "Organic fruit matter",
            "detected_category": "organic",
            "confidence": 0.95,
            "condition": "normal",
            "hazard_tags": [],
            "is_uncertain": False,
            "ai_explanation": "Compostable organic matter that enriches soil organic carbon."
        },
        {
            "triggers": ["coffee grounds", "used coffee", "espresso puck"],
            "item_name": "Used Coffee Grounds",
            "material": "Organic coffee bean residue",
            "detected_category": "organic",
            "confidence": 0.96,
            "condition": "normal",
            "hazard_tags": [],
            "is_uncertain": False,
            "ai_explanation": "High-nitrogen organic matter ideal for aerobic microbial composting."
        },
        {
            "triggers": ["eggshell", "egg shells", "egg shell"],
            "item_name": "Eggshells",
            "material": "Calcium carbonate organic shell",
            "detected_category": "organic",
            "confidence": 0.94,
            "condition": "normal",
            "hazard_tags": [],
            "is_uncertain": False,
            "ai_explanation": "Mineral-rich organic waste that breaks down to fortify compost calcium levels."
        },
        {
            "triggers": ["vegetable scraps", "carrot peel", "lettuce", "onion skin"],
            "item_name": "Vegetable Trimmings",
            "material": "Organic vegetable matter",
            "detected_category": "organic",
            "confidence": 0.94,
            "condition": "normal",
            "hazard_tags": [],
            "is_uncertain": False,
            "ai_explanation": "High moisture organic kitchen waste readily accepted in municipal green bins."
        },

        # GENERAL / SOILED
        {
            "triggers": ["greasy pizza box", "pizza box", "oily box", "soiled cardboard"],
            "item_name": "Greasy Pizza Box",
            "material": "Food-soiled corrugated cardboard",
            "detected_category": "general",
            "confidence": 0.88,
            "condition": "greasy",
            "hazard_tags": [],
            "is_uncertain": False,
            "ai_explanation": "Grease and melted cheese residue prevent paper fibers from bonding during water-based pulping."
        },
        {
            "triggers": ["styrofoam cup", "styrofoam", "polystyrene", "foam container", "takeout foam"],
            "item_name": "Expanded Polystyrene (Styrofoam) Container",
            "material": "Expanded Polystyrene (#6 EPS)",
            "detected_category": "general",
            "confidence": 0.92,
            "condition": "normal",
            "hazard_tags": [],
            "is_uncertain": False,
            "ai_explanation": "Expanded foam polystyrene is too light and low-density for cost-effective curbside sorting."
        },
        {
            "triggers": ["chip bag", "potato chip bag", "crisp packet", "candy wrapper", "snack wrapper"],
            "item_name": "Multi-layer Metallized Snack Wrapper",
            "material": "Laminated polypropylene and aluminum film",
            "detected_category": "general",
            "confidence": 0.90,
            "condition": "normal",
            "hazard_tags": [],
            "is_uncertain": False,
            "ai_explanation": "Composite multi-material film cannot be mechanically separated in recycling facilities."
        },
        {
            "triggers": ["broken ceramic mug", "ceramic mug", "broken plate", "porcelain", "pyrex"],
            "item_name": "Broken Ceramic Dish / Mug",
            "material": "Fired ceramic / silicate clay",
            "detected_category": "general",
            "confidence": 0.89,
            "condition": "broken",
            "hazard_tags": ["sharp"],
            "is_uncertain": False,
            "ai_explanation": "Ceramics have a much higher melting point than container glass and will ruin glass batches."
        },
        {
            "triggers": ["diaper", "nappy", "dirty diaper", "sanitary pad", "tampon"],
            "item_name": "Sanitary Diaper / Hygiene Product",
            "material": "Superabsorbent polymer, non-woven fabric, organic waste",
            "detected_category": "general",
            "confidence": 0.96,
            "condition": "soiled",
            "hazard_tags": [],
            "is_uncertain": False,
            "ai_explanation": "Mixed polymer and organic personal hygiene waste must be landfilled."
        },
    ]

    def classify(
        self,
        text: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
        image_type: Optional[str] = None,
        raw_query: Optional[str] = None,
    ) -> WasteAnalysisInput:
        query = (text or raw_query or "").strip().lower()

        # Case 1: Image provided WITHOUT text description in mock mode
        if not query and image_bytes:
            return WasteAnalysisInput(
                item_name="Unverified Waste Item (Image Only)",
                material="Unidentified from Image",
                detected_category="general",
                confidence=0.35,  # Low confidence enforces Rule 1 Uncertainty Guard
                condition="unknown",
                hazard_tags=[],
                is_uncertain=True,
                ai_explanation=(
                    "In mock mode, image pixels cannot be visually analyzed locally. "
                    "Real computer vision inference requires Amazon Bedrock (multimodal Claude 3 or Nova). "
                    "For local mock testing, provide a text description alongside the photo or test with 1-click presets. "
                    "Safe uncertainty protocols applied."
                ),
                raw_query=None,
            )

        # Case 2: Neither text nor image provided (empty query)
        if not query:
            return WasteAnalysisInput(
                item_name="Unidentified Waste Item",
                material="Unknown / Indeterminate",
                detected_category="general",
                confidence=0.30,
                condition="unknown",
                hazard_tags=[],
                is_uncertain=True,
                ai_explanation="No waste description or image content was provided.",
                raw_query="",
            )

        # Case 3: Text provided (with or without image)
        # Check for gibberish / low-information inputs
        if len(query) < 3 or re.match(r"^[^a-zA-Z0-9]+$", query) or query in ["something", "stuff", "thing", "unknown", "asdf", "asdfghjk", "trash", "waste"]:
            return WasteAnalysisInput(
                item_name="Unidentified Waste Item",
                material="Unknown / Indeterminate",
                detected_category="general",
                confidence=0.35,  # Low confidence triggers safety uncertainty rule
                condition="unknown",
                hazard_tags=[],
                is_uncertain=True,
                ai_explanation="The provided description does not contain sufficient descriptive characteristics to accurately determine material or waste stream.",
                raw_query=query,
            )

        # Match against database
        for entry in self.DATABASE:
            for trigger in entry["triggers"]:
                if trigger in query:
                    explanation = entry["ai_explanation"]
                    if image_bytes:
                        explanation += f" (Mock mode: classified using accompanying text description '{text or query}'; image attached)."
                    return WasteAnalysisInput(
                        item_name=entry["item_name"],
                        material=entry["material"],
                        detected_category=entry["detected_category"],
                        confidence=entry["confidence"],
                        condition=entry.get("condition", "normal"),
                        hazard_tags=entry.get("hazard_tags", []),
                        is_uncertain=entry.get("is_uncertain", False),
                        ai_explanation=explanation,
                        raw_query=query,
                    )

        # If keyword has generic hazardous indicators
        if any(w in query for w in ["acid", "toxic", "poison", "chemical", "bulb", "battery", "oil"]):
            explanation = "Identified potential chemical or toxic hazards requiring specialized handling."
            if image_bytes:
                explanation += " (Mock mode: text-assisted classification; image attached)."
            return WasteAnalysisInput(
                item_name=f"Potential Hazardous Item ({query.title()})",
                material="Suspected hazardous chemical/electronic formulation",
                detected_category="hazardous",
                confidence=0.72,
                condition="normal",
                hazard_tags=["toxic"],
                is_uncertain=False,
                ai_explanation=explanation,
                raw_query=query,
            )

        # If keyword has generic organic indicators
        if any(w in query for w in ["leaf", "grass", "plant", "food", "meat", "scrap", "peel"]):
            explanation = "Identified as plant or food-derived organic matter."
            if image_bytes:
                explanation += " (Mock mode: text-assisted classification; image attached)."
            return WasteAnalysisInput(
                item_name=f"Organic Matter ({query.title()})",
                material="Biodegradable biomass",
                detected_category="organic",
                confidence=0.82,
                condition="normal",
                hazard_tags=[],
                is_uncertain=False,
                ai_explanation=explanation,
                raw_query=query,
            )

        # Fallback for unrecognizable specific item: return safe uncertain prediction
        explanation = "Unfamiliar waste description with indeterminate recyclable composition."
        if image_bytes:
            explanation += " (Note: Local mock mode does not perform computer vision inference on image pixels; Amazon Bedrock is required for visual analysis)."
        return WasteAnalysisInput(
            item_name=f"Unverified Item ('{query[:40]}')",
            material="Indeterminate composite",
            detected_category="general",
            confidence=0.48,  # Intentionally low to enforce safe handling
            condition="unknown",
            hazard_tags=[],
            is_uncertain=True,
            ai_explanation=explanation,
            raw_query=query,
        )


class BedrockClassifier(BaseClassifier):
    """Production Amazon Bedrock multimodal classifier.

    Uses Bedrock Converse API or Claude Messages API with zero hardcoded credentials,
    relying on standard AWS IAM role / environment resolution.
    """

    SYSTEM_PROMPT = """You are an expert environmental and waste management computer vision system.
Analyze the user's waste item description and/or uploaded photo.
Classify the waste strictly into one of four core categories:
1. "recyclable" (clean metal, paper, cardboard, rigid plastics, glass)
2. "organic" (food scraps, vegetable peelings, garden clippings, compostable biomass)
3. "hazardous" (batteries, chemicals, e-waste, paints, fluorescent bulbs, motor oil, medical sharps)
4. "general" (non-recyclable plastics, dirty ceramics, styrofoam, metallized film, soiled trash)

If the item is ambiguous, vague, low quality, or cannot be recognized reliably, you MUST set is_uncertain to true and confidence below 0.60. NEVER invent high confidence scores.

Respond ONLY with valid JSON matching this schema:
{
  "item_name": "Precise name of identified waste item",
  "material": "Primary material (e.g., #1 PET Plastic, Corrugated Cardboard, Lithium Electrolyte)",
  "detected_category": "recyclable" | "organic" | "hazardous" | "general",
  "confidence": 0.0 to 1.0 (float),
  "condition": "clean" | "greasy" | "soiled" | "broken" | "battery_included" | "normal",
  "hazard_tags": ["flammable", "toxic", "sharp", "corrosive", "biohazard"] (or empty list),
  "is_uncertain": true | false,
  "ai_explanation": "Brief reasoning for classification"
}
"""

    def __init__(self, region_name: Optional[str] = None, model_id: Optional[str] = None):
        self.region_name = region_name or DEFAULT_AWS_REGION
        self.model_id = model_id or DEFAULT_BEDROCK_MODEL
        self._client = None
        self._fallback_mock = MockClassifier()

    def _get_client(self):
        if self._client is None:
            import boto3
            self._client = boto3.client("bedrock-runtime", region_name=self.region_name)
        return self._client

    def classify(
        self,
        text: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
        image_type: Optional[str] = None,
        raw_query: Optional[str] = None,
    ) -> WasteAnalysisInput:
        """Invoke Amazon Bedrock to identify the waste item."""
        try:
            client = self._get_client()

            # Construct Converse API content blocks
            content_blocks = []

            # Add image block if provided
            if image_bytes:
                fmt = "jpeg"
                if image_type:
                    if "png" in image_type.lower():
                        fmt = "png"
                    elif "webp" in image_type.lower():
                        fmt = "webp"
                    elif "gif" in image_type.lower():
                        fmt = "gif"

                content_blocks.append({
                    "image": {
                        "format": fmt,
                        "source": {
                            "bytes": image_bytes
                        }
                    }
                })

            prompt_text = text or raw_query or "Analyze this waste item in the image."
            content_blocks.append({"text": prompt_text})

            response = client.converse(
                modelId=self.model_id,
                system=[{"text": self.SYSTEM_PROMPT}],
                messages=[
                    {
                        "role": "user",
                        "content": content_blocks
                    }
                ],
                inferenceConfig={
                    "maxTokens": 600,
                    "temperature": 0.1,  # Low temperature for factual consistency
                }
            )

            # Parse Bedrock response
            output_message = response.get("output", {}).get("message", {})
            response_contents = output_message.get("content", [])
            full_text = "".join(part.get("text", "") for part in response_contents)

            return self._parse_llm_json(full_text, prompt_text)

        except Exception as err:
            logger.warning(
                f"Bedrock invocation failed ({err.__class__.__name__}: {err}). "
                "Safely switching to mock/fallback classifier."
            )
            return self._fallback_mock.classify(
                text=text,
                image_bytes=image_bytes,
                image_type=image_type,
                raw_query=raw_query,
            )

    def _parse_llm_json(self, raw_llm_response: str, query: str) -> WasteAnalysisInput:
        """Extract and validate JSON from LLM output."""
        try:
            # Extract JSON substring
            match = re.search(r"\{.*\}", raw_llm_response, re.DOTALL)
            if not match:
                raise ValueError("No JSON block found in LLM output")

            data = json.loads(match.group(0))

            category = data.get("detected_category", "general").lower()
            if category not in {"recyclable", "organic", "hazardous", "general"}:
                category = "general"

            confidence = float(data.get("confidence", 0.5))
            confidence = max(0.0, min(1.0, confidence))

            return WasteAnalysisInput(
                item_name=data.get("item_name", "Waste Item"),
                material=data.get("material", "Mixed Material"),
                detected_category=category,
                confidence=confidence,
                condition=data.get("condition", "normal"),
                hazard_tags=data.get("hazard_tags", []),
                is_uncertain=bool(data.get("is_uncertain", False)),
                ai_explanation=data.get("ai_explanation"),
                raw_query=query,
            )
        except Exception as e:
            logger.error(f"Error parsing Bedrock JSON response: {e}")
            return WasteAnalysisInput(
                item_name="Unidentified Waste Item",
                material="Unknown",
                detected_category="general",
                confidence=0.40,
                condition="unknown",
                hazard_tags=[],
                is_uncertain=True,
                ai_explanation="Failed to parse AI structured response safely.",
                raw_query=query,
            )


def get_classifier(force_mock: bool = False) -> BaseClassifier:
    """Factory function returning the appropriate classifier based on configuration."""
    is_mock_env = os.getenv("MOCK_MODE", "false").lower() in ("true", "1", "yes")

    # If mock is explicitly requested or MOCK_MODE environment variable is set
    if force_mock or is_mock_env:
        logger.info("Using MockClassifier (mock mode active)")
        return MockClassifier()

    # Check if AWS credentials exist or Bedrock is configured
    has_aws_creds = bool(
        os.getenv("AWS_ACCESS_KEY_ID")
        or os.getenv("AWS_CONTAINER_CREDENTIALS_RELATIVE_URI")
        or os.getenv("AWS_WEB_IDENTITY_TOKEN_FILE")
        or os.getenv("AWS_PROFILE")
        or os.path.exists(os.path.expanduser("~/.aws/credentials"))
    )

    if not has_aws_creds and not os.getenv("AWS_EXECUTION_ENV"):
        logger.info("No AWS credentials detected; defaulting to MockClassifier")
        return MockClassifier()

    return BedrockClassifier()
