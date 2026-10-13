from pathlib import Path

import pandas as pd
import joblib
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay
)


# 1. Project paths
BASE_DIR = Path(__file__).resolve().parent

DATA_PATH = BASE_DIR / "Data" / "Processed" / "News_dataset.csv"
MODEL_DIR = BASE_DIR / "models"

MODEL_PATH = MODEL_DIR / "final_svm_model.pkl"
VECTORIZER_PATH = MODEL_DIR / "final_tfidf_vectorizer.pkl"

MODEL_DIR.mkdir(parents=True, exist_ok=True)


# 2. Load dataset
print("Loading dataset...")
print("Dataset path:", DATA_PATH)

data = pd.read_csv(DATA_PATH)

# Check required columns
required_columns = ["title", "text", "subject", "label"]
missing_columns = [
    column for column in required_columns
    if column not in data.columns
]

if missing_columns:
    raise ValueError(
        f"Dataset is missing columns: {missing_columns}"
    )

data["label"] = (
    data["label"].astype(str).str.strip().str.upper()
)

data = data[
    data["label"].isin(["FAKE", "REAL"])
].copy()

data["content"] = (
    data["title"].fillna("").astype(str)
    + " "
    + data["text"].fillna("").astype(str)
).str.strip()

data = data[data["content"] != ""].copy()

data = data.drop_duplicates(
    subset=["content"]
).copy()

print("Articles after removing duplicates:", len(data))

if data["label"].nunique() != 2:
    raise ValueError(
        "Dataset must contain both FAKE and REAL labels."
    )


# 3. Prepare features and labels
X = data["content"]
y = data["label"]

print("\nTotal articles:", len(data))
print("\nLabel counts:")
print(y.value_counts())

print("\nUnique labels:", sorted(data["label"].unique()))


# 4. Check label distribution by subject
print("\n========== LABEL DISTRIBUTION BY SUBJECT ==========")

print(
    pd.crosstab(
        data["subject"].fillna("UNKNOWN"),
        data["label"]
    )
)


# 5. Split into training and testing data
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\nTraining articles:", len(X_train))
print("Testing articles:", len(X_test))


# 6. Convert text to TF-IDF features
print("\nPreparing text data...")

vectorizer = TfidfVectorizer(
    max_features=5000,
    stop_words="english"
)

X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)


# 7. Train calibrated Linear SVM
print("\nTraining model...")

model = CalibratedClassifierCV(
    LinearSVC(),
    cv=3
)

model.fit(X_train_tfidf, y_train)


# 8. Evaluate model
print("\n========== MODEL EVALUATION ==========")

predictions = model.predict(X_test_tfidf)

accuracy = accuracy_score(
    y_test,
    predictions
)

print(f"\nAccuracy: {accuracy * 100:.2f}%")

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        predictions,
        labels=["FAKE", "REAL"],
        zero_division=0
    )
)


# 9. Confusion matrix
cm = confusion_matrix(
    y_test,
    predictions,
    labels=["FAKE", "REAL"]
)

print("\nConfusion Matrix:")
print(cm)

display = ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=["FAKE", "REAL"]
)

display.plot(values_format="d")

plt.title("Fake News DNA Analyzer - Confusion Matrix")
plt.tight_layout()

chart_path = BASE_DIR / "confusion_matrix.png"

plt.savefig(
    chart_path,
    dpi=150
)

plt.close()

print("\nConfusion matrix saved:", chart_path)


# 10. Save model and vectorizer
joblib.dump(model, MODEL_PATH)
joblib.dump(vectorizer, VECTORIZER_PATH)

print("\n========== MODEL SAVED ==========")
print("Model:", MODEL_PATH)
print("Vectorizer:", VECTORIZER_PATH)


# 11. Test example statements
test_texts = [
    "The Earth revolves around the Sun.",
    "The Sun revolves around the Earth.",
    "Water freezes at 0 degrees Celsius.",
    "The Earth is flat.",
    "The Moon orbits the Earth.",
    "Humans can breathe underwater without equipment."
]

print("\n========== SAMPLE PREDICTIONS ==========")

for text in test_texts:
    text_vector = vectorizer.transform([text])

    prediction = model.predict(text_vector)[0]
    probabilities = model.predict_proba(text_vector)[0]

    print("\nText:", text)
    print("Prediction:", prediction)

    print(
        "Probabilities:",
        {
            label: round(float(probability) * 100, 2)
            for label, probability in zip(
                model.classes_,
                probabilities
            )
        }
    )


# 12. Duplicate checks
print("\n========== DUPLICATE NEWS CHECK ==========")

print(
    "Duplicate articles:",
    data["content"].duplicated().sum()
)

print(
    "Conflicting labels:",
    (
        data.groupby("content")["label"].nunique() > 1
    ).sum()
)

print("\n========== PROCESS COMPLETED ==========")