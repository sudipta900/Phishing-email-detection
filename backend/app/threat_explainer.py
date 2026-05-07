import re

THREAT_PATTERNS = {
    "Urgency": [
        "urgent",
        "immediately",
        "act now",
        "expires",
        "suspended"
    ],

    "Credential Harvesting": [
        "password",
        "verify account",
        "confirm account",
        "bank details"
    ],

    "Prize Scam": [
        "winner",
        "lottery",
        "claim reward",
        "free gift"
    ],

    "Suspicious Links": [
        "http://",
        "https://"
    ]
}

def explain_threats(text: str):

    findings = []

    lowered = text.lower()

    for category, keywords in THREAT_PATTERNS.items():

        matched = []

        for kw in keywords:
            if kw in lowered:
                matched.append(kw)

        if matched:
            findings.append({
                "category": category,
                "matches": matched
            })

    return findings