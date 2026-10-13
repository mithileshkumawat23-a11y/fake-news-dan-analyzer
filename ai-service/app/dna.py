def generate_dna(risk_signal, confidence, claims_count, evidence_count):

    if confidence >= 0.80:
        confidence_level = "HIGH"
    elif confidence >= 0.60:
        confidence_level = "MEDIUM"
    else:
        confidence_level = "LOW"

    return {
        "risk_signal": risk_signal,
        "confidence": round(confidence, 4),
        "confidence_percentage": round(confidence * 100, 2),
        "confidence_level": confidence_level,
        "claims_detected": claims_count,
        "evidence_found": evidence_count
    }