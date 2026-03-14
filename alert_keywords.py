# Red Alert Keywords for Medical Pillars

## Pharmacy Pillar Keywords
PHARMACY_ALERT_KEYWORDS = [
    "pain", "dizzy", "dizziness", "nausea", "vomiting", "rash", "itching",
    "swelling", "bleeding", "bruising", "fever", "chills", "headache",
    "reaction", "allergic", "side effect", "worse", "emergency", "help",
    "hospital", "doctor", "urgent", "severe", "can't breathe", "chest pain",
    "difficulty breathing", "unconscious", "seizure", "convulsion"
]

## Hospital Pillar Keywords
HOSPITAL_ALERT_KEYWORDS = [
    "pain", "dizzy", "dizziness", "nausea", "vomiting", "rash", "itching",
    "swelling", "bleeding", "bruising", "fever", "chills", "headache",
    "reaction", "allergic", "complication", "worse", "emergency", "help",
    "critical", "urgent", "severe", "can't breathe", "chest pain",
    "difficulty breathing", "unconscious", "seizure", "convulsion",
    "infection", "discharge", "wound", "stitches", "bandage"
]

## Combined Alert Keywords (for general use)
ALL_ALERT_KEYWORDS = list(set(PHARMACY_ALERT_KEYWORDS + HOSPITAL_ALERT_KEYWORDS))

def check_for_alert_keywords(text, pillar="general"):
    """
    Check if text contains red alert keywords
    Returns: (has_alert, matched_keywords)
    """
    text_lower = text.lower()

    if pillar == "pharmacy":
        keywords = PHARMACY_ALERT_KEYWORDS
    elif pillar == "hospital":
        keywords = HOSPITAL_ALERT_KEYWORDS
    else:
        keywords = ALL_ALERT_KEYWORDS

    matched = [kw for kw in keywords if kw in text_lower]
    return len(matched) > 0, matched