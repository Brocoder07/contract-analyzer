from __future__ import annotations

from typing import Optional


HINDI_RECOMMENDATION_MAP: dict[str, str] = {
    "auto_renewal": "ऑटो-रिन्यूअल क्लॉज में स्पष्ट नोटिस अवधि और लिखित समाप्ति प्रक्रिया जोड़ें।",
    "liability": "दायित्व की सीमा (liability cap) स्पष्ट करें और अप्रत्यक्ष/परिणामी नुकसान को बाहर करें।",
    "termination": "समाप्ति (termination) की शर्तें, नोटिस अवधि और उपचार (cure period) स्पष्ट करें।",
    "ip_ownership": "IP स्वामित्व के दायरे, pre-existing IP और उपयोग अधिकार (license) स्पष्ट करें।",
    "indemnification": "इंडेम्निटी क्लॉज का दायरा सीमित करें और पारस्परिक (mutual) सुरक्षा जोड़ें।",
    "confidentiality": "गोपनीयता क्लॉज में डेटा उपयोग, अपवाद और अवधि स्पष्ट रूप से परिभाषित करें।",
    "termination_for_convenience": "Termination for Convenience को द्विपक्षीय बनाएं या उचित नोटिस अवधि व निकास शर्तें जोड़ें।",
    "uncapped_liability": "Uncapped liability को सीमित करें और अधिकतम वित्तीय सीमा निर्धारित करें।",
    "cap_on_liability": "Liability cap का दायरा स्पष्ट करें और carve-outs को सीमित/परिभाषित करें।",
    "liquidated_damages": "Liquidated damages को उचित, मापनीय और अनुपातिक सीमा में रखें।",
    "non_compete": "Non-compete की अवधि, क्षेत्र और दायरा युक्तिसंगत व सीमित करें।",
    "exclusivity": "Exclusivity क्लॉज में स्पष्ट अपवाद, अवधि और प्रदर्शन-आधारित शर्तें जोड़ें।",
    "covenant_not_to_sue": "Covenant not to sue के दायरे और अपवाद (fraud, willful misconduct) स्पष्ट करें।",
    "minimum_commitment": "Minimum commitment को यथार्थवादी बनाएं और force majeure/volume variance अपवाद जोड़ें।",
    "ip_ownership_assignment": "IP assignment से पहले pre-existing IP और license-back अधिकार सुरक्षित करें।",
    "no_solicit_of_employees": "No-solicit क्लॉज की अवधि और लागू दायरे को सीमित व स्पष्ट करें।",
    "non_disparagement": "Non-disparagement में mutual language और कानूनी प्रकटीकरण अपवाद जोड़ें।",
    "anti_assignment": "Assignment के लिए prior consent को ‘not unreasonably withheld’ भाषा से संतुलित करें।",
    "change_of_control": "Change of control पर termination/consent अधिकारों की स्पष्ट और संतुलित शर्तें जोड़ें।",
    "rofr_rofo_rofn": "ROFR/ROFO/ROFN प्रक्रिया, समय-सीमा और नोटिस तंत्र स्पष्ट करें।",
    "post_termination_services": "Post-termination services की अवधि, शुल्क और सेवा-स्तर लिखित रूप से तय करें।",
}


def _normalise_risk_type(risk_type: Optional[str]) -> str:
    if not risk_type:
        return ""
    return (
        risk_type.strip()
        .lower()
        .replace("-", "_")
        .replace("/", "_")
        .replace(" ", "_")
    )


def get_hindi_recommendation(risk_type: Optional[str], fallback_text: str) -> str:
    key = _normalise_risk_type(risk_type)
    return HINDI_RECOMMENDATION_MAP.get(key, fallback_text)
