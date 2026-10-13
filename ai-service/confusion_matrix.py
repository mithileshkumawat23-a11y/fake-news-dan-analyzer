import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn.metrics import classification_report
from pathlib import Path

# Load dataset
BASE_DIR = Path(__file__).resolve().parent
data = pd.read_csv(BASE_DIR / "Data" / "Processed" / "News_dataset.csv")

# Combine title and text
data["content"] = data["title"].fillna("") + " " + data["text"].fillna("")

X = data["content"]
y = data["label"]

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

# TF-IDF
vectorizer = TfidfVectorizer(
    max_features=5000,
    stop_words="english"
)

X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

# Linear SVM
model = LinearSVC()
model.fit(X_train_tfidf, y_train)

# Prediction
predictions = model.predict(X_test_tfidf)

# Confusion Matrix
cm = confusion_matrix(y_test, predictions, labels=["FAKE", "REAL"])

print("Confusion Matrix:")
print(cm)

# Classification Report
print("\nClassification Report:")
print(classification_report(y_test, predictions, target_names=["FAKE", "REAL"]))

# Display
display = ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=["FAKE", "REAL"]
)

display.plot()
plt.title("Fake News DNA Analyzer - Linear SVM")
plt.show()