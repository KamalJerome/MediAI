"""
Safety checker module for detecting and blocking unsafe medical requests.
Uses context-aware and intent-based filtering for smarter detection.
"""

import re
from typing import Tuple

# HARMFUL INTENT PATTERNS - These indicate requests for medical advice/treatment
HARMFUL_DIAGNOSIS_PATTERNS = [
    r"do i have", r"am i suffering", r"could i have", r"might i have",
    r"what disease", r"what condition", r"what's wrong with me",
    r"symptoms mean", r"symptoms indicate", r"diagnose.*symptom"
]

HARMFUL_MEDICATION_PATTERNS = [
    r"prescribe.*me", r"give.*me.*medication", r"how.*many.*take",
    r"how.*much.*dose", r"is.*safe.*take", r"can i take", r"should i take",
    r"dosage.*for.*me", r"dose.*for.*me", r"what.*medicine.*should"
]

HARMFUL_TREATMENT_PATTERNS = [
    r"how.*to.*treat", r"treat.*my.*\w+", r"cure.*my", r"heal.*my",
    r"how.*to.*recover", r"therapy.*for.*me", r"surgery.*needed",
    r"procedure.*for.*me"
]

EMERGENCY_KEYWORDS = [
    "emergency", "urgent", "critical", "severe", "dying", "dead", "hospital",
    "call 911", "call ambulance", "poison", "overdose", "suicide", "hurt myself",
    "blood", "heart attack", "stroke", "can't breathe", "difficulty breathing"
]

# ALLOWED CONTEXT KEYWORDS - These indicate educational/informational intent
ALLOWED_CONTEXT_KEYWORDS = [
    "explain", "what is", "tell me about", "help me understand",
    "what does", "describe", "information about", "educational"
]

# Warning messages
DIAGNOSIS_WARNING = """
⚠️ **I Cannot Provide Medical Diagnosis**

I cannot diagnose medical conditions based on symptoms or personal information. Please consult a qualified healthcare professional or visit a doctor for proper medical diagnosis.

If you need immediate medical attention, please call emergency services or visit the nearest hospital.
"""

MEDICATION_WARNING = """
⚠️ **I Cannot Provide Medication or Dosage Advice**

I cannot prescribe medications or provide dosage recommendations for you. Only licensed healthcare providers can prescribe medications based on your individual health situation.

Please consult with your doctor or pharmacist for medication-related questions. Do not self-medicate without professional guidance.
"""

EMERGENCY_WARNING = """
🚨 **EMERGENCY - IMMEDIATE ACTION REQUIRED**

This appears to be a medical emergency. **Please seek immediate medical help:**
- Call local emergency number
- Visit the nearest emergency room
- Call poison control for poisoning cases

Do not rely on this chatbot for emergency situations.
"""

TREATMENT_WARNING = """
⚠️ **I Cannot Provide Treatment Advice**

I cannot provide personalized treatment or therapeutic advice for your specific condition. Treatment plans must be customized by qualified healthcare professionals based on your individual health assessment.

Please consult with your doctor, nurse, or other qualified healthcare providers for treatment guidance.
"""


def is_unsafe_request(user_input: str, has_documents: bool = False) -> Tuple[bool, str]:
    """
    Check if the user request is unsafe using intelligent context-aware detection.
    
    Args:
        user_input: The user's message
        has_documents: Whether the user has uploaded documents (context for RAG)
        
    Returns:
        Tuple of (is_unsafe: bool, warning_message: str)
    """
    user_input_lower = user_input.lower()
    
    # Emergency check (highest priority - always block)
    for keyword in EMERGENCY_KEYWORDS:
        if keyword in user_input_lower:
            return True, EMERGENCY_WARNING
    
    # If user has context (uploaded documents), allow medication/prescription mentions
    # for explaining their own medical documents
    if has_documents:
        # Still block explicit harmful intent patterns
        for pattern in HARMFUL_MEDICATION_PATTERNS:
            if re.search(pattern, user_input_lower):
                return True, MEDICATION_WARNING
        
        for pattern in HARMFUL_DIAGNOSIS_PATTERNS:
            if re.search(pattern, user_input_lower):
                return True, DIAGNOSIS_WARNING
        
        for pattern in HARMFUL_TREATMENT_PATTERNS:
            if re.search(pattern, user_input_lower):
                return True, TREATMENT_WARNING
        
        # If none of the harmful patterns matched, allow the request (even with prescription/medication words)
        return False, ""
    
    # No documents context - use stricter pattern matching
    
    # Diagnosis check
    for pattern in HARMFUL_DIAGNOSIS_PATTERNS:
        if re.search(pattern, user_input_lower):
            return True, DIAGNOSIS_WARNING
    
    # Medication check - but allow mentions in informational context
    if not _is_informational_context(user_input_lower):
        for pattern in HARMFUL_MEDICATION_PATTERNS:
            if re.search(pattern, user_input_lower):
                return True, MEDICATION_WARNING
    
    # Treatment check
    for pattern in HARMFUL_TREATMENT_PATTERNS:
        if re.search(pattern, user_input_lower):
            return True, TREATMENT_WARNING
    
    return False, ""


def _is_informational_context(user_input_lower: str) -> bool:
    """
    Detect if the query is asking for educational information rather than personal advice.
    
    Args:
        user_input_lower: Lowercase user input
        
    Returns:
        True if query appears to be informational/educational
    """
    for keyword in ALLOWED_CONTEXT_KEYWORDS:
        if keyword in user_input_lower:
            return True
    
    # Check for generic/general questions (not about "me" or "my")
    if not re.search(r"\b(me|my|mine|i have|i am)\b", user_input_lower):
        # Generic question about medical topics is usually informational
        return True
    
    return False


def get_safety_guidelines() -> str:
    """Get safety guidelines message for display."""
    return """
**Safety Guidelines:**
- I provide general medical information only
- I cannot diagnose conditions
- I cannot prescribe medications or dosages
- I cannot provide treatment plans
- For emergencies, call 911 immediately
- Always consult healthcare professionals for medical decisions

By using this chatbot, you acknowledge you understand these limitations.
"""
