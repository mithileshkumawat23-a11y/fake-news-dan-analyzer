import re


def extract_claims(text):
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())

    claims = []

    for sentence in sentences:
        sentence = sentence.strip()

        if len(sentence.split()) >= 5:
            claims.append(sentence)

    return claims