import joblib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

model = joblib.load(BASE_DIR / "models" / "final_svm_model.pkl")
vectorizer = joblib.load(
    BASE_DIR / "models" / "final_tfidf_vectorizer.pkl"
)

test_texts = [
    "The Earth revolves around the Sun.",
    "The Sun revolves around the Earth.",
    "Water freezes at 0 degrees Celsius.",
    "The Earth is flat.",
    "The Moon orbits the Earth.",
    "Humans can breathe underwater without equipment."
]

print("Model classes:", model.classes_)

for text in test_texts:
    vector = vectorizer.transform([text])
    prediction = model.predict(vector)[0]
    probabilities = model.predict_proba(vector)[0]

    print("\nText:", text)
    print("Prediction:", prediction)
    print({
        str(label): round(float(prob) * 100, 2)
        for label, prob in zip(model.classes_, probabilities)
    })