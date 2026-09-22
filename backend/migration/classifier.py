from typing import Dict, Any, Optional, Tuple
from backend.migration.cloud_rules import match_cloud_rule
from backend.migration.desktop_rules import match_desktop_rule
from backend.migration.hybrid_rules import match_hybrid_rule

class ActionClassifier:
    """
    Evaluates individual A360 actions and classifies them into:
    - Power Automate Cloud
    - Power Automate Desktop
    - Hybrid
    - Manual Review
    """

    @staticmethod
    def classify_action(
        command: str,
        action: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
        context_has_cloud: bool = False,
        context_has_desktop: bool = False
    ) -> Tuple[str, str, float]:
        """
        Returns (platform, classification_reason, confidence)
        Platform is one of: "Power Automate Cloud", "Power Automate Desktop", "Hybrid", "Manual Review"
        """
        attrs = attributes or {}
        cmd_clean = (command or "").strip()

        # 1. Check Hybrid Rules (e.g. runTask bridging)
        hybrid_match = match_hybrid_rule(cmd_clean, action, attrs, context_has_cloud, context_has_desktop)
        if hybrid_match:
            _, reason, conf = hybrid_match
            return "Hybrid", reason, conf

        # 2. Check Desktop Rules
        desktop_match = match_desktop_rule(cmd_clean, action, attrs)
        if desktop_match:
            _, reason, conf = desktop_match
            return "Power Automate Desktop", reason, conf

        # 3. Check Cloud Rules
        cloud_match = match_cloud_rule(cmd_clean, action, attrs)
        if cloud_match:
            _, reason, conf = cloud_match
            return "Power Automate Cloud", reason, conf

        # 4. If command is unknown or unsupported, follow Section 30 Unknown Command Policy
        return (
            "Manual Review",
            f"Command '{cmd_clean}' has no deterministic Power Automate mapping rule. Requires RPA architect review.",
            0.30
        )
