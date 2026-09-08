import logging
from typing import Any

logger = logging.getLogger(__name__)

def apply_verification_gate(ai_decision: dict, candidates: list[dict], min_deterministic_score: float = 40.0) -> dict:
    """
    Applies the deterministic rejection gate.
    ai_decision: {"decision": "<url> or NONE/FAILED", "confidence": int, "justification": str}
    candidates: The scored list of candidates provided to the AI.
    Returns the final status object to be returned to the downstream flow.
    """
    decision = ai_decision.get("decision", "NONE")
    confidence = ai_decision.get("confidence", 0)
    justification = ai_decision.get("justification", "")
    
    if decision == "FAILED":
        return {
            "url": None,
            "status": "NOT_CHECKED",
            "confidence": 0,
            "reasoning": f"AI provider failure: {justification}"
        }
        
    if decision == "NONE":
        return {
            "url": None,
            "status": "UNVERIFIED",
            "confidence": 0,
            "reasoning": f"AI abstained: {justification}"
        }
        
    # AI selected a URL. We must cross-check it against the deterministic candidates.
    matched_candidate = None
    for c in candidates:
        if c.get("url", "") == decision:
            matched_candidate = c
            break
            
    if not matched_candidate:
        logger.warning(f"Rejection Gate: AI hallucinated URL {decision}")
        return {
            "url": decision,
            "status": "REJECTED_LOW_CONFIDENCE",
            "confidence": confidence,
            "reasoning": "Rejected: AI selected a URL not present in the candidate pool."
        }
        
    candidate_score = matched_candidate.get("score", 0)
    if candidate_score < min_deterministic_score:
        logger.warning(f"Rejection Gate: AI selected weak candidate {decision} (score: {candidate_score})")
        return {
            "url": decision,
            "status": "REJECTED_LOW_CONFIDENCE",
            "confidence": confidence,
            "reasoning": f"Rejected: Candidate deterministic score {candidate_score} is below threshold."
        }
        
    if confidence < 70:
        logger.warning(f"Rejection Gate: AI selected candidate {decision} but confidence {confidence} too low")
        return {
            "url": decision,
            "status": "REJECTED_LOW_CONFIDENCE",
            "confidence": confidence,
            "reasoning": f"Rejected: AI confidence {confidence} is below threshold."
        }
        
    # Passed all checks
    return {
        "url": decision,
        "status": "VERIFIED",
        "confidence": confidence,
        "reasoning": f"Verified by AI (score: {candidate_score}, conf: {confidence}). Justification: {justification}"
    }

