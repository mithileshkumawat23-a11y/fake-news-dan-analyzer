from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib

from app.claims import extract_claims
from app.evidence import (
    search_evidence,
    verify_evidence,
    fetch_reference_sources
)
from app.dna import generate_dna
from app.explainability import explain_prediction


# Create FastAPI application
app = FastAPI(
    title="Fake News DNA Analyzer",
    version="1.0"
)


# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Load trained model and vectorizer using stable paths
BASE_DIR = Path(__file__).resolve().parent.parent

model = joblib.load(
    BASE_DIR / "models" / "final_svm_model.pkl"
)

vectorizer = joblib.load(
    BASE_DIR / "models" / "final_tfidf_vectorizer.pkl"
)


# Request format
class NewsRequest(BaseModel):
    text: str


# Home endpoint
@app.get("/")
def home():
    return {
        "message": "Fake News DNA Analyzer API is running"
    }


# Health endpoint
@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# Analyze news endpoint
@app.post("/analyze")
def analyze_news(request: NewsRequest):

    try:
        text = request.text.strip()

        if not text:
            return {
                "error": "Please enter some news text."
            }
        
    
        

        # 1. ML prediction
        text_vector = vectorizer.transform([text])
        prediction = str(model.predict(text_vector)[0])
        probabilities = model.predict_proba(text_vector)[0]

        class_probabilities = {
            str(label): round(float(probability), 4)
            for label, probability in zip(
                model.classes_, probabilities
            )
        }

        confidence = float(max(probabilities))

        # ML result is a prediction, not a fact-check verdict
        risk_signal = (
            "HIGH" if prediction == "FAKE"
            else "LOW"
        )

        # 2. Extract claims
        claims = extract_claims(text)

        evidence = []
        verification = []
        reference_sources = []

        # 3. Collect evidence and verify each claim
        for claim in claims:

            claim_evidence = search_evidence(claim) or []
            evidence.extend(claim_evidence)

            references = fetch_reference_sources(claim) or []

            for reference in references:
                reference["claim"] = claim

            reference_sources.extend(references)

            result = verify_evidence(
                claim,
                claim_evidence
            )

            verification.append(result)

        # Do not claim the whole article is verified
        # merely because the classifier is confident.
        verified_results = [
            item for item in verification
            if isinstance(item, dict)
        ]

        fact_check_status = "UNVERIFIED"

        # 4. Explain the ML prediction
        explanation = explain_prediction(
            model,
            vectorizer,
            text
        )

        # 5. Generate DNA report from ML signal
        dna_report = generate_dna(
            risk_signal,
            confidence,
            len(claims),
            len(evidence)
        )

        return {
            "prediction": prediction,
            "fact_check_status": fact_check_status,
            "confidence_note": (
                "ML confidence measures the classifier's "
                "confidence in its learned text patterns. "
                "It does not establish factual truth. "
                "Check the evidence and sources separately."
            ),
            "risk_signal": risk_signal,
            "confidence": round(confidence, 4),
            "class_probabilities": class_probabilities,
            "claims": claims,
            "evidence": evidence,
            "verification": verification,
            "reference_sources": reference_sources,
            "explanation": explanation,
            "dna_report": dna_report,
            "message": "Analysis completed; factual status has not been independently established."
        }

    except Exception as e:
        return {
            "error": str(e)
        }