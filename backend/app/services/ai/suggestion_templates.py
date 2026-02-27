"""
Suggestion templates for contract risk mitigation
Provides rule-based recommendations for each risk type
"""

from app.models.schemas import RiskType

SUGGESTION_TEMPLATES = {
    RiskType.AUTO_RENEWAL: [
        {
            "text": "Add an explicit opt-out notification period (e.g., 60-90 days before renewal)",
            "rationale": "Prevents automatic renewal without consent and gives adequate time to evaluate continuation",
            "priority": 1
        },
        {
            "text": "Require written confirmation before each renewal period",
            "rationale": "Ensures active agreement continuation rather than passive acceptance",
            "priority": 1
        },
        {
            "text": "Include a clause allowing termination at the end of any renewal period with 30 days notice",
            "rationale": "Provides flexibility to exit the contract after trying the service",
            "priority": 2
        },
        {
            "text": "Negotiate for annual renewals instead of longer periods",
            "rationale": "Shorter renewal periods provide more frequent exit opportunities",
            "priority": 2
        }
    ],
    
    RiskType.LIABILITY: [
        {
            "text": "Negotiate for mutual liability caps instead of one-sided limitations",
            "rationale": "Balances risk between both parties and ensures fair protection",
            "priority": 1
        },
        {
            "text": "Exclude gross negligence and willful misconduct from liability caps",
            "rationale": "Maintains accountability for serious violations and intentional harm",
            "priority": 1
        },
        {
            "text": "Ensure liability cap is at least equal to contract value or reasonable multiple thereof",
            "rationale": "Provides meaningful recourse in case of breach or damages",
            "priority": 2
        },
        {
            "text": "Carve out data breaches, IP infringement, and confidentiality violations from limitations",
            "rationale": "Protects against high-impact risks that could cause significant business harm",
            "priority": 1
        }
    ],
    
    RiskType.TERMINATION: [
        {
            "text": "Add termination for convenience clause with 30-60 days notice",
            "rationale": "Allows exit from underperforming relationships without proving cause",
            "priority": 1
        },
        {
            "text": "Ensure termination rights are mutual and balanced between parties",
            "rationale": "Prevents one party from having unfair advantage to exit while other is locked in",
            "priority": 1
        },
        {
            "text": "Include material breach termination with cure period (15-30 days)",
            "rationale": "Provides opportunity to fix issues before contract termination",
            "priority": 2
        },
        {
            "text": "Clarify post-termination obligations including data return and transition assistance",
            "rationale": "Ensures smooth exit and protects business continuity",
            "priority": 2
        }
    ],
    
    RiskType.INDEMNIFICATION: [
        {
            "text": "Limit indemnification to third-party claims arising from indemnifying party's breach",
            "rationale": "Ensures you only indemnify for your own actions, not the other party's conduct",
            "priority": 1
        },
        {
            "text": "Add mutual indemnification clauses to balance obligations",
            "rationale": "Both parties protect each other from their respective liabilities",
            "priority": 1
        },
        {
            "text": "Require notice and opportunity to control defense of indemnified claims",
            "rationale": "Allows you to manage legal strategy for claims you're paying for",
            "priority": 2
        },
        {
            "text": "Cap indemnification obligations consistent with liability limitations",
            "rationale": "Prevents unlimited exposure beyond agreed liability caps",
            "priority": 2
        }
    ],
    
    RiskType.CONFIDENTIALITY: [
        {
            "text": "Add specific carve-outs for independently developed information",
            "rationale": "Protects information you develop without using the other party's confidential data",
            "priority": 1
        },
        {
            "text": "Limit confidentiality period to 3-5 years post-disclosure",
            "rationale": "Prevents indefinite restrictions that may outlive business value of information",
            "priority": 2
        },
        {
            "text": "Exclude information that becomes publicly available through no fault of receiving party",
            "rationale": "Standard protection ensuring you're not liable for public knowledge",
            "priority": 2
        },
        {
            "text": "Include exception for disclosures required by law or court order",
            "rationale": "Protects against liability when legally compelled to disclose",
            "priority": 1
        }
    ],
    
    RiskType.IP_OWNERSHIP: [
        {
            "text": "Ensure work product and deliverables are explicitly assigned to your company",
            "rationale": "Clarifies ownership of materials you're paying to create",
            "priority": 1
        },
        {
            "text": "Exclude pre-existing IP and background technology from assignment clauses",
            "rationale": "Protects IP you bring to the relationship from being transferred",
            "priority": 1
        },
        {
            "text": "Add representations that vendor owns or has rights to license all provided IP",
            "rationale": "Protects against third-party infringement claims",
            "priority": 1
        },
        {
            "text": "Include clear license grants for any IP that isn't assigned",
            "rationale": "Ensures you can use necessary technology without ownership transfer",
            "priority": 2
        },
        {
            "text": "Negotiate for IP warranty and indemnification against infringement claims",
            "rationale": "Shifts risk of IP disputes to the party providing the IP",
            "priority": 1
        }
    ],
}

def get_suggestions_for_risk(risk_type: RiskType) -> list[dict]:
    """
    Retrieve suggestion templates for a specific risk type
    
    Args:
        risk_type: The type of risk to get suggestions for
        
    Returns:
        List of suggestion dictionaries with text, rationale, and priority
    """
    return SUGGESTION_TEMPLATES.get(risk_type, [])

def get_all_risk_types_with_templates() -> list[RiskType]:
    """
    Get list of all risk types that have suggestion templates
    
    Returns:
        List of RiskType enums that have templates defined
    """
    return list(SUGGESTION_TEMPLATES.keys())

