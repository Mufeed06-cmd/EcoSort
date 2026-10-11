"""Disposal Rules Engine for AI Waste Segregation Advisor.

Separates deterministic environmental disposal logic and safety protocols
from raw AI visual/textual identification.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


UNCERTAINTY_CONFIDENCE_THRESHOLD = 0.65
HIGH_CONFIDENCE_THRESHOLD = 0.85

VALID_CATEGORIES = {"recyclable", "organic", "hazardous", "general"}


@dataclass
class WasteAnalysisInput:
    """Standardized intermediate representation produced by AI classifier."""
    item_name: str
    material: str = "Unknown"
    detected_category: str = "general"
    confidence: float = 0.50
    condition: str = "normal"  # "clean", "greasy", "soiled", "broken", "battery_included", "normal"
    hazard_tags: List[str] = field(default_factory=list)
    is_uncertain: bool = False
    ai_explanation: Optional[str] = None
    raw_query: Optional[str] = None


@dataclass
class WasteAnalysisOutput:
    """Standardized output returned to client."""
    status: str
    item_name: str
    category: str
    is_uncertain: bool
    confidence: float
    confidence_level: str  # "high", "medium", "low"
    summary: str
    material: str
    disposal_instructions: List[str]
    safety_warnings: List[str]
    preparation_steps: List[str]
    alternative_options: List[str]
    environmental_impact: str
    rules_applied: List[str]
    source: str = "rules_engine"
    ai_explanation: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "item_name": self.item_name,
            "category": self.category,
            "is_uncertain": self.is_uncertain,
            "confidence": round(self.confidence, 2),
            "confidence_level": self.confidence_level,
            "summary": self.summary,
            "material": self.material,
            "disposal_instructions": self.disposal_instructions,
            "safety_warnings": self.safety_warnings,
            "preparation_steps": self.preparation_steps,
            "alternative_options": self.alternative_options,
            "environmental_impact": self.environmental_impact,
            "rules_applied": self.rules_applied,
            "source": self.source,
            "ai_explanation": self.ai_explanation,
        }


# Keywords that trigger hazardous safety overrides
HAZARD_KEYWORDS = [
    "battery", "lithium", "lead-acid", "accumulator", "chemical", "pesticide",
    "insecticide", "solvent", "thinner", "motor oil", "engine oil", "antifreeze",
    "coolant", "fluorescent", "cfl", "mercury", "paint", "varnish", "bleach",
    "ammonia", "aerosol", "propane", "butane", "gas canister", "firework",
    "syringe", "needle", "lancet", "biohazard", "pharmaceutical", "medication",
    "pill", "antibiotic", "e-waste", "electronics", "circuit board"
]

# Organic keywords
ORGANIC_KEYWORDS = [
    "food", "fruit", "vegetable", "peel", "banana", "apple", "orange", "egg",
    "eggshell", "coffee", "grounds", "tea", "bread", "crust", "meat", "bone",
    "rice", "leaves", "grass", "plant", "flower", "compostable"
]

# Recyclable keywords (when clean)
RECYCLABLE_KEYWORDS = [
    "aluminum", "aluminium", "tin can", "soda can", "beverage can", "cardboard",
    "paper", "box", "newspaper", "magazine", "glass bottle", "glass jar",
    "pet bottle", "plastic bottle", "hdpe", "milk jug", "water bottle"
]

# Non-recyclable / General waste keywords
GENERAL_KEYWORDS = [
    "styrofoam", "polystyrene", "ceramic", "porcelain", "pyrex", "drinking glass",
    "mirror", "chip bag", "crisp packet", "candy wrapper", "foil pouch",
    "diaper", "nappy", "sanitary", "cigarette", "vacuum dust", "cotton swab",
    "wax paper", "carbon paper"
]


class DisposalRulesEngine:
    """Evaluates AI waste classifications using strict safety and environmental rules."""

    @staticmethod
    def get_confidence_level(confidence: float) -> str:
        if confidence >= HIGH_CONFIDENCE_THRESHOLD:
            return "high"
        if confidence >= UNCERTAINTY_CONFIDENCE_THRESHOLD:
            return "medium"
        return "low"

    def evaluate(self, analysis: WasteAnalysisInput, source: str = "bedrock") -> WasteAnalysisOutput:
        """Apply rule cascade to the parsed AI analysis."""
        rules_applied: List[str] = []
        safety_warnings: List[str] = []
        disposal_instructions: List[str] = []
        preparation_steps: List[str] = []
        alternative_options: List[str] = []

        item_lower = (analysis.item_name or "").lower()
        material_lower = (analysis.material or "").lower()
        combined_text = f"{item_lower} {material_lower} {analysis.raw_query or ''}".lower()

        # Check for explicit or detected hazard triggers
        is_hazard = (
            analysis.detected_category == "hazardous"
            or bool(analysis.hazard_tags)
            or any(kw in combined_text for kw in HAZARD_KEYWORDS)
        )

        # Check uncertainty condition
        is_uncertain = (
            analysis.is_uncertain
            or analysis.confidence < UNCERTAINTY_CONFIDENCE_THRESHOLD
            or analysis.detected_category not in VALID_CATEGORIES
            or "unknown" in item_lower
            or "unidentified" in item_lower
        )

        confidence = max(0.05, min(0.99, analysis.confidence))
        if is_uncertain and confidence > 0.65:
            # Never invent high confidence for an uncertain item
            confidence = 0.50

        # RULE 1: Safety & Uncertainty Protection
        if is_uncertain:
            rules_applied.append(
                f"Rule 1 [Uncertainty Guard]: Confidence ({confidence:.2f}) below threshold ({UNCERTAINTY_CONFIDENCE_THRESHOLD}) or input ambiguous."
            )
            return self._handle_uncertain_waste(
                analysis=analysis,
                confidence=confidence,
                is_hazard=is_hazard,
                rules_applied=rules_applied,
                source=source,
            )

        # RULE 2: Hazardous Waste Override (Highest Priority)
        if is_hazard:
            rules_applied.append("Rule 2 [Hazardous Safety Override]: Hazardous item or constituent detected.")
            return self._handle_hazardous_waste(
                analysis=analysis,
                confidence=confidence,
                combined_text=combined_text,
                rules_applied=rules_applied,
                source=source,
            )

        # RULE 3: Contamination & Soiling Guard (Greasy/Soiled Cardboard, Plastics, Paper)
        if analysis.condition in ("greasy", "soiled") or "greas" in combined_text or "soiled" in combined_text:
            rules_applied.append("Rule 3 [Contamination Guard]: Item is soiled with grease or organic residue.")
            return self._handle_soiled_waste(
                analysis=analysis,
                confidence=confidence,
                combined_text=combined_text,
                rules_applied=rules_applied,
                source=source,
            )

        # RULE 4: Specific Material Disqualifiers (Styrofoam, Broken Ceramics, Composite Film)
        if any(kw in combined_text for kw in GENERAL_KEYWORDS):
            rules_applied.append("Rule 4 [Material Non-Recyclable Rule]: Material cannot be processed by standard curbside facilities.")
            return self._handle_general_waste(
                analysis=analysis,
                confidence=confidence,
                combined_text=combined_text,
                rules_applied=rules_applied,
                source=source,
            )

        # RULE 5: Organic / Compostable Waste
        if analysis.detected_category == "organic" or any(kw in combined_text for kw in ORGANIC_KEYWORDS):
            rules_applied.append("Rule 5 [Organic Composting Rule]: Biodegradable organic matter confirmed.")
            return self._handle_organic_waste(
                analysis=analysis,
                confidence=confidence,
                combined_text=combined_text,
                rules_applied=rules_applied,
                source=source,
            )

        # RULE 6: Clean Recyclable Stream
        if analysis.detected_category == "recyclable" or any(kw in combined_text for kw in RECYCLABLE_KEYWORDS):
            rules_applied.append("Rule 6 [Clean Recyclable Rule]: Valid dry recyclable material verified.")
            return self._handle_recyclable_waste(
                analysis=analysis,
                confidence=confidence,
                combined_text=combined_text,
                rules_applied=rules_applied,
                source=source,
            )

        # RULE 7: Default General Waste (Safe fallback for non-hazardous standard items)
        rules_applied.append("Rule 7 [Default Municipal General Waste]: No recyclable or compost stream matched safely.")
        return self._handle_general_waste(
            analysis=analysis,
            confidence=confidence,
            combined_text=combined_text,
            rules_applied=rules_applied,
            source=source,
        )

    def _handle_uncertain_waste(
        self,
        analysis: WasteAnalysisInput,
        confidence: float,
        is_hazard: bool,
        rules_applied: List[str],
        source: str,
    ) -> WasteAnalysisOutput:
        """Safe handling for uncertain or ambiguous items. Never recommends recycling unverified items."""
        if is_hazard:
            category = "hazardous"
            rules_applied.append("Sub-rule: Potential hazardous indicators present in ambiguous item.")
            summary = (
                f"Potentially hazardous material detected for '{analysis.item_name}', but specific classification is uncertain. "
                "Defaulting to strict hazardous waste precautionary protocols."
            )
            warnings = [
                "CAUTION: Potential chemical, electrical, or toxic hazard.",
                "DO NOT dispose of in regular trash, recycling bins, or down drains.",
                "DO NOT puncture, incinerate, or expose to heat or water."
            ]
            instructions = [
                "Keep the item in a sealed, labeled container in a cool, ventilated area.",
                "Take directly to your municipal Household Hazardous Waste (HHW) drop-off facility.",
                "Consult the facility technician for proper identification before disposal."
            ]
        else:
            category = "general"
            rules_applied.append("Sub-rule: Excluded from recyclable and compostable streams to prevent batch contamination.")
            summary = (
                f"The item '{analysis.item_name}' could not be definitively identified with high confidence ({confidence:.0%}). "
                "To prevent contaminating recycling streams or compost batches, safe non-hazardous disposal is advised."
            )
            warnings = [
                "Uncertain identification: Placing unknown materials in recycling can contaminate entire processing batches (wishcycling).",
                "Do not incinerate or flush unknown items."
            ]
            instructions = [
                "If the item is ordinary non-chemical household scrap, place it in the general/landfill bin.",
                "If there is any chance it contains batteries, wiring, or chemicals, treat it as hazardous waste.",
                "Check for manufacturer recycling codes (e.g. resin identification triangle) before disposal."
            ]

        return WasteAnalysisOutput(
            status="success",
            item_name=analysis.item_name or "Unidentified Item",
            category=category,
            is_uncertain=True,
            confidence=confidence,
            confidence_level=self.get_confidence_level(confidence),
            summary=summary,
            material=analysis.material or "Uncertain / Mixed",
            disposal_instructions=instructions,
            safety_warnings=warnings,
            preparation_steps=["Isolate from clean recyclables and food compost", "Inspect for manufacturer labels or hazard symbols"],
            alternative_options=["Use your local city council waste search tool or app to look up specific localized regulations."],
            environmental_impact="Preventing recycling contamination saves clean batches from being diverted to landfills.",
            rules_applied=rules_applied,
            source=source,
            ai_explanation=analysis.ai_explanation,
        )

    def _handle_hazardous_waste(
        self,
        analysis: WasteAnalysisInput,
        confidence: float,
        combined_text: str,
        rules_applied: List[str],
        source: str,
    ) -> WasteAnalysisOutput:
        """Strict protocols for hazardous, electronic, or toxic items."""
        warnings: List[str] = [
            "DANGER / HAZARD: Do not place in curbside trash or curbside recycling.",
            "Never incinerate, crush, or pour down plumbing or storm drains."
        ]
        instructions: List[str] = []
        prep: List[str] = []
        alts: List[str] = []

        if "battery" in combined_text or "lithium" in combined_text:
            rules_applied.append("Sub-rule [Battery Safety]: Terminal insulation and fire prevention required.")
            warnings.append("FIRE HAZARD: Lithium-ion and metal batteries can spark or experience thermal runaway if crushed.")
            instructions.append("Tape both terminals (+ and -) with clear packing tape or electrical tape.")
            instructions.append("Place each battery into a separate plastic bag.")
            instructions.append("Drop off at a certified battery recycling depot, Home Depot, Best Buy, or Call2Recycle drop box.")
            prep.append("Insulate terminals with non-conductive tape")
            alts.append("Call2Recycle partner locator: find nearest drop-off box.")
        elif any(k in combined_text for k in ["paint", "solvent", "varnish", "oil", "chemical", "pesticide"]):
            rules_applied.append("Sub-rule [Chemical Safety]: Containment and spill prevention required.")
            warnings.append("TOXIC / FLAMMABLE: Vapors and liquid run-off contaminate groundwater.")
            instructions.append("Keep in original container with label intact and lid tightly secured.")
            instructions.append("Transport upright in a cardboard box lined with newspaper or plastic.")
            instructions.append("Take to municipal Household Hazardous Waste (HHW) collection day.")
            prep.append("Ensure container is tightly sealed")
            alts.append("Check if local community paint-swap or reuse programs accept leftover paint.")
        elif any(k in combined_text for k in ["cfl", "fluorescent", "mercury"]):
            rules_applied.append("Sub-rule [Mercury Safety]: Fragile vapor containment.")
            warnings.append("Contains mercury vapor: Handle gently to avoid breakage.")
            instructions.append("Do not break the glass tube or bulb.")
            instructions.append("Place inside a padded cardboard box or original sleeve.")
            instructions.append("Drop off at municipal e-waste/hardware store bulb collection kiosk.")
            prep.append("Wrap bulb in bubble wrap or cardboard")
        elif any(k in combined_text for k in ["needle", "syringe", "lancet", "biohazard", "pharmaceutical"]):
            rules_applied.append("Sub-rule [Bio-Medical Safety]: Sharps & medication protocol.")
            warnings.append("BIOHAZARD / SHARPS: Risk of puncture and medication contamination of waterways.")
            instructions.append("Place sharps immediately into a rigid FDA-cleared sharps container or thick detergent bottle.")
            instructions.append("Never throw loose needles in household trash or recycling.")
            instructions.append("Return unused medicines to pharmacy take-back kiosks.")
            prep.append("Seal in puncture-resistant container")
            alts.append("Check with local pharmacy for prescription take-back programs.")
        else:
            # General e-waste or miscellaneous hazard
            rules_applied.append("Sub-rule [Specialty E-Waste / Hazardous]: Designated drop-off routing.")
            instructions.append("Deliver to a municipal specialized waste recovery center.")
            instructions.append("Do not dismantle or compromise the outer casing.")
            prep.append("Keep intact and dry")

        return WasteAnalysisOutput(
            status="success",
            item_name=analysis.item_name,
            category="hazardous",
            is_uncertain=False,
            confidence=confidence,
            confidence_level=self.get_confidence_level(confidence),
            summary=f"'{analysis.item_name}' contains hazardous or regulated constituents requiring specialized disposal.",
            material=analysis.material or "Hazardous / Regulated Material",
            disposal_instructions=instructions,
            safety_warnings=warnings,
            preparation_steps=prep or ["Keep in secure packaging"],
            alternative_options=alts or ["Contact local municipal hazardous waste hotline."],
            environmental_impact="Prevents toxic heavy metals, corrosives, and flammable chemicals from leaching into groundwater and soils.",
            rules_applied=rules_applied,
            source=source,
            ai_explanation=analysis.ai_explanation,
        )

    def _handle_soiled_waste(
        self,
        analysis: WasteAnalysisInput,
        confidence: float,
        combined_text: str,
        rules_applied: List[str],
        source: str,
    ) -> WasteAnalysisOutput:
        """Handles greasy pizza boxes, food-stained paper, or unwashed containers."""
        instructions: List[str] = []
        warnings: List[str] = [
            "CONTAMINATION RISK: Grease and food residue permanently degrade recycled paper fibers.",
        ]
        prep: List[str] = []
        alts: List[str] = []

        if "pizza" in combined_text or "cardboard" in combined_text or "paper" in combined_text:
            rules_applied.append("Sub-rule [Cardboard Partition]: Separate clean lid from greasy base.")
            category = "organic" if ("compost" in combined_text or "food" in combined_text) else "general"
            instructions.append("Tear off the clean cardboard lid: Place the clean top in the blue recycling bin.")
            instructions.append("Take the greasy, food-stained bottom: If your city allows food-soiled paper in green/compost bins, compost it; otherwise, place in the general waste bin.")
            prep.append("Tear box in half along the crease")
            alts.append("Compost greasy sections in municipal food-waste programs that accept soiled paper.")
            summary = f"'{analysis.item_name}' is food-soiled. Clean portions can be recycled, but greasy portions belong in compost or general trash."
        else:
            # Soiled plastic or general container
            rules_applied.append("Sub-rule [Container Rinse Requirement]: Rinse to restore recyclability.")
            category = "recyclable"
            instructions.append("Rinse thoroughly with cold or gray water to remove food particles.")
            instructions.append("Shake dry before tossing into the recycling bin.")
            instructions.append("If grease or residue cannot be cleaned, discard in general waste.")
            prep.extend(["Scrape food residue", "Rinse and shake dry"])
            summary = f"'{analysis.item_name}' requires rinsing before entering the recycling stream."

        return WasteAnalysisOutput(
            status="success",
            item_name=analysis.item_name,
            category=category,
            is_uncertain=False,
            confidence=confidence,
            confidence_level=self.get_confidence_level(confidence),
            summary=summary,
            material=analysis.material or "Soiled Packaging / Paper",
            disposal_instructions=instructions,
            safety_warnings=warnings,
            preparation_steps=prep,
            alternative_options=alts,
            environmental_impact="Keeps clean recycling loads pure, preventing truckloads of paper from being rejected at processing mills.",
            rules_applied=rules_applied,
            source=source,
            ai_explanation=analysis.ai_explanation,
        )

    def _handle_organic_waste(
        self,
        analysis: WasteAnalysisInput,
        confidence: float,
        combined_text: str,
        rules_applied: List[str],
        source: str,
    ) -> WasteAnalysisOutput:
        """Handles compostable organic food scraps and garden waste."""
        instructions: List[str] = [
            "Place in your household organic compost caddy or municipal green bin.",
            "Keep free of plastic bags, twist ties, or elastic bands."
        ]
        warnings: List[str] = []
        prep: List[str] = []

        if any(k in combined_text for k in ["fruit", "banana", "apple", "orange", "lemon"]):
            rules_applied.append("Sub-rule [Produce Stickers]: Non-biodegradable PLU stickers must be removed.")
            prep.append("Peel off plastic produce price/barcode stickers (PLU stickers do not decompose).")
            warnings.append("Note: Fruit stickers are plastic and do NOT compost. Remove them first.")

        if "tea" in combined_text:
            rules_applied.append("Sub-rule [Teabag Staple/Mesh]: Check for nylon mesh or metal staples.")
            prep.append("Check if teabag contains plastic/nylon sealant or staples before composting.")

        return WasteAnalysisOutput(
            status="success",
            item_name=analysis.item_name,
            category="organic",
            is_uncertain=False,
            confidence=confidence,
            confidence_level=self.get_confidence_level(confidence),
            summary=f"'{analysis.item_name}' is biodegradable organic matter suitable for composting.",
            material=analysis.material or "Organic / Biodegradable",
            disposal_instructions=instructions,
            safety_warnings=warnings,
            preparation_steps=prep or ["Ensure free of synthetic contaminants"],
            alternative_options=[
                "Backyard vermicomposting (worm bin)",
                "Bokashi fermentation",
                "Community garden compost drop-off"
            ],
            environmental_impact="Composting diverts organic waste from landfills, eliminating methane emissions and restoring nutrient-rich humus to soil.",
            rules_applied=rules_applied,
            source=source,
            ai_explanation=analysis.ai_explanation,
        )

    def _handle_recyclable_waste(
        self,
        analysis: WasteAnalysisInput,
        confidence: float,
        combined_text: str,
        rules_applied: List[str],
        source: str,
    ) -> WasteAnalysisOutput:
        """Handles verified clean recyclable materials."""
        instructions: List[str] = []
        prep: List[str] = []
        warnings: List[str] = []

        if any(k in combined_text for k in ["can", "aluminum", "tin", "metal"]):
            rules_applied.append("Sub-rule [Metal Recyclable]: Highly infinitely recyclable.")
            instructions.append("Empty all liquids completely.")
            instructions.append("Rinse lightly to remove sticky residue.")
            instructions.append("Place in your standard blue recycling bin (no need to crush unless saving space).")
            prep.extend(["Empty contents completely", "Quick rinse"])
        elif any(k in combined_text for k in ["bottle", "jar", "glass"]):
            rules_applied.append("Sub-rule [Glass Recyclable]: Remove lids; keep intact.")
            instructions.append("Rinse residue out of the bottle or jar.")
            instructions.append("Remove metal or plastic caps and recycle separately.")
            instructions.append("Do not break the glass; intact containers are sorted more efficiently.")
            prep.extend(["Rinse clean", "Separate lid"])
            warnings.append("Do not include drinking glasses, Pyrex, or window panes (different melting point).")
        elif any(k in combined_text for k in ["paper", "cardboard", "box"]):
            rules_applied.append("Sub-rule [Paper/Cardboard]: Keep dry and flatten.")
            instructions.append("Flatten cardboard boxes to save space in the collection truck.")
            instructions.append("Remove excessive plastic packaging tape and plastic inserts.")
            instructions.append("Ensure paper is completely dry; wet paper cannot be sorted.")
            prep.extend(["Flatten boxes", "Remove plastic packing peanuts"])
        else:
            # Rigid Plastics (#1, #2, #5)
            rules_applied.append("Sub-rule [Rigid Plastics]: Rinse and replace cap if requested.")
            instructions.append("Rinse clean of contents.")
            instructions.append("Replace screw cap securely on the bottle (prevents caps from jamming machinery).")
            prep.extend(["Rinse container", "Screw cap back on"])

        return WasteAnalysisOutput(
            status="success",
            item_name=analysis.item_name,
            category="recyclable",
            is_uncertain=False,
            confidence=confidence,
            confidence_level=self.get_confidence_level(confidence),
            summary=f"'{analysis.item_name}' is a recyclable commodity. Proper preparation ensures high recovery rates.",
            material=analysis.material or "Recyclable Commodity",
            disposal_instructions=instructions,
            safety_warnings=warnings,
            preparation_steps=prep or ["Ensure item is clean and dry"],
            alternative_options=["Redeem at local container deposit depot for cash refund where available."],
            environmental_impact="Recycling reduces virgin extraction of bauxite, petroleum, and timber while cutting industrial greenhouse gas emissions by up to 95%.",
            rules_applied=rules_applied,
            source=source,
            ai_explanation=analysis.ai_explanation,
        )

    def _handle_general_waste(
        self,
        analysis: WasteAnalysisInput,
        confidence: float,
        combined_text: str,
        rules_applied: List[str],
        source: str,
    ) -> WasteAnalysisOutput:
        """Handles non-recyclable, non-compostable general municipal waste."""
        instructions: List[str] = [
            "Place inside a sturdy waste bag and tie securely.",
            "Dispose in the black/gray municipal general landfill bin."
        ]
        warnings: List[str] = []
        prep: List[str] = []

        if "broken" in combined_text or "glass" in combined_text or "ceramic" in combined_text:
            rules_applied.append("Sub-rule [Sharp Object Protection]: Wrap broken fragments.")
            warnings.append("SHARP HAZARD: Broken ceramics or glassware can pierce waste bags and injure sanitation workers.")
            instructions.insert(0, "Wrap broken pieces in several layers of newspaper or cardboard before placing in the trash bag.")
            prep.append("Wrap safely in newspaper or tape between cardboard")

        if "styrofoam" in combined_text or "polystyrene" in combined_text:
            rules_applied.append("Sub-rule [Polystyrene / Styrofoam]: Exclude from curbside recycling.")
            warnings.append("Styrofoam (#6 EPS) is not accepted in standard curbside single-stream recycling.")
            alts = ["Check if specialized local EPS recycling drop-offs exist in your area."]
        else:
            alts = ["Consider reusable alternatives to reduce landfill footprint."]

        return WasteAnalysisOutput(
            status="success",
            item_name=analysis.item_name,
            category="general",
            is_uncertain=False,
            confidence=confidence,
            confidence_level=self.get_confidence_level(confidence),
            summary=f"'{analysis.item_name}' cannot currently be recycled or composted in standard municipal facilities. Destined for safe general landfill disposal.",
            material=analysis.material or "Mixed / Non-Recyclable Waste",
            disposal_instructions=instructions,
            safety_warnings=warnings,
            preparation_steps=prep or ["Bag and tie securely"],
            alternative_options=alts,
            environmental_impact="Proper containment prevents litter, microplastic pollution, and sanitation worker injuries.",
            rules_applied=rules_applied,
            source=source,
            ai_explanation=analysis.ai_explanation,
        )
