import shap
import pandas as pd
from pathlib import Path


def explain_prediction(model, vectorizer, text):

    text_vector = vectorizer.transform([text])

    # Find the class predicted by the final calibrated model
    prediction = model.predict(text_vector)[0]
    classes = list(model.classes_)

    # Use the first fitted LinearSVC for explanation
    base_model = model.calibrated_classifiers_[0].estimator

    # Load background data relative to this file
    base_dir = Path(__file__).resolve().parent.parent
    data_path = base_dir / "Data" / "Processed" / "News_dataset.csv"

    if not data_path.exists():
        data_path = base_dir / "data" / "processed" / "news_dataset.csv"

    data = pd.read_csv(data_path)

    background_text = (
        data["title"].fillna("").astype(str)
        + " "
        + data["text"].fillna("").astype(str)
    )

    background_text = background_text.sample(
        n=min(100, len(background_text)),
        random_state=42
    )

    background_vector = vectorizer.transform(background_text)

    explainer = shap.LinearExplainer(
        base_model,
        background_vector
    )

    shap_values = explainer(text_vector)
    values = shap_values.values

    if len(values.shape) == 3:
        values = values[0, :, 0]
    else:
        values = values[0]

    feature_names = vectorizer.get_feature_names_out()
    important_features = []

    # Determine the class direction used by the binary LinearSVC
    base_classes = list(base_model.classes_)

    if len(base_classes) != 2:
        return {
            "method": "SHAP",
            "top_features": [],
            "message": "Binary class explanation is not available."
        }

    for i, value in enumerate(values):

        if text_vector[0, i] == 0:
            continue

        score = float(value)

        # LinearSVC positive decision scores point toward classes_[1].
        # SHAP signs must be interpreted against that class ordering.
        if base_classes[1] == prediction:
            predicted_class_influence = score
        else:
            predicted_class_influence = -score

        influence = (
            str(prediction)
            if predicted_class_influence > 0
            else str(base_classes[0] if prediction == base_classes[1]
                     else base_classes[1])
        )

        important_features.append({
            "word": feature_names[i],
            "influence": influence,
            "score": round(predicted_class_influence, 4)
        })

    important_features.sort(
        key=lambda item: abs(item["score"]),
        reverse=True
    )

    return {
        "method": "SHAP",
        "predicted_class": str(prediction),
        "top_features": important_features[:10]
    }