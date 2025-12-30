from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List
import json
import os

# -------------------------------
# 1. Pydantic schema
# -------------------------------
class DropoutAnalysis(BaseModel):
    dropout_probability: float = Field(
        description="Float between 0 and 1 indicating dropout risk"
    )
    risk_level: str = Field(
        description="One of: Low, Moderate, High"
    )
    psychological_reasons: List[str] = Field(
        description="List of psychological factors contributing to risk"
    )
    student_strengths: List[str] = Field(
        description="List of student strengths identified"
    )
    recommended_interventions: List[str] = Field(
        description="List of specific interventions"
    )


# -------------------------------
# 2. Setup Google Gemini AI (FREE!)
# -------------------------------
# Get your free API key from: https://aistudio.google.com/app/apikey
# Then set it: export GOOGLE_API_KEY='your-key-here'

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    max_output_tokens=1024,
    google_api_key="AIzaSyDec0wNwk2aTDQezBzuLX7HGz_MnVcz9sA",
)

# --------------------------------
# 3. System + user prompts
# --------------------------------
SYSTEM_PROMPT = """
You are an educational psychologist. You receive RAW_FORM_RESPONSE_JSON (a.txt dictionary).
You MUST do three things exactly:

1) Compute normalized construct scores from the JSON (0.0 - 1.0) for these constructs:
   - motivation, stress, self_efficacy, engagement, goal_clarity
   For any missing construct, compute by averaging available questions for that construct;
   if no data, assume 0.5.

2) Compute an exact numeric dropout_probability using this deterministic formula (no deviation):
   - base = 0.0
   - base += 0.35 * (1 - motivation)       # low motivation increases risk
   - base += 0.30 * stress                 # high stress increases risk
   - base += 0.20 * (1 - self_efficacy)    # low self-efficacy increases risk
   - base += 0.10 * (1 - engagement)       # low engagement increases risk
   - base += 0.05 * (1 - goal_clarity)
   - dropout_probability = clamp(base, 0.0, 1.0)
   Round dropout_probability to 2 decimal places.

3) Derive risk_level from dropout_probability:
   - [0.00, 0.30] -> "Low"
   - (0.30, 0.60] -> "Moderate"
   - (0.60, 1.00] -> "High"

4) Provide psychological_reasons: each reason MUST cite the exact input key
   or raw snippet that motivated it.
   e.txt.g. "q_family_pressure -> 'My parents want me to marry soon.' indicates family pressure"

5) Output ONLY valid JSON that matches the Pydantic schema 
   and do NOT include any extra keys or commentary.
   

Follow the exact formula above. Do NOT invent another scoring method.
"""

# Few-shot examples
FEWSHOT = """
Example 1 INPUT:
{{ "q_motivation_1": 5, "q_motivation_2": 4, "q_stress_1": 1, "q_goal_clarity": 5 }}

Example 1 OUTPUT:
{{
  "dropout_probability": 0.06,
  "risk_level": "Low",
  "psychological_reasons": ["q_stress_1 -> '1' indicates low stress", "q_motivation_1 -> '5' indicates high motivation"],
  "student_strengths": ["High motivation", "Clear goals"],
  "recommended_interventions": ["Periodic mentor check-ins"]
}}

Example 2 INPUT:
{{ "q_motivation_1": 2, "q_stress_1": 5, "q_self_efficacy_1": 2, "q_goal_clarity": 1 }}

Example 2 OUTPUT:
{{
  "dropout_probability": 0.80,
  "risk_level": "High",
  "psychological_reasons": ["q_stress_1 -> '5' indicates high stress", "q_motivation_1 -> '2' indicates low motivation", "q_goal_clarity -> '1' indicates poor goal clarity"],
  "student_strengths": ["None clearly stated"],
  "recommended_interventions": ["Immediate counselling for stress", "Mentor assigned weekly"]
}}
"""

USER_PROMPT_TEMPLATE = """
Here is the RAW_FORM_RESPONSE_JSON. Compute construct scores,
apply the exact formula in SYSTEM PROMPT, and return ONLY the JSON defined by the schema.

RAW_FORM_RESPONSE_JSON:
{form_response_json}
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("system", FEWSHOT),
    ("human", USER_PROMPT_TEMPLATE)
])


# -------------------------
# 4. Build the LCEL chain
# -------------------------
chain = prompt | llm


def analyze_student_dropout_risk(form_response: dict) -> dict:
    """
    Analyze student dropout risk based on raw Google Form response using Google Gemini AI.
    """
    try:
        form_response_json = json.dumps(form_response, indent=2)

        response = chain.invoke({
            "form_response_json": form_response_json
        })

        response_text = response.content if hasattr(response, "content") else str(response)

        try:
            start_idx = response_text.find("{")
            end_idx = response_text.rfind("}") + 1

            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                analysis_result = json.loads(json_str)
            else:
                analysis_result = json.loads(response_text)

        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON response: {e}")
            print(f"Raw response: {response_text}")
            raise

        return analysis_result

    except Exception as e:
        print(f"Error analyzing student data: {e}")
        raise


def analyze_batch_students(form_responses: List[dict]) -> List[dict]:
    """
    Analyze multiple students in batch.
    """
    results = []

    for i, form_response in enumerate(form_responses):
        print(f"Analyzing student {i + 1}/{len(form_responses)}...")

        try:
            result = analyze_student_dropout_risk(form_response)
            result["student_id"] = form_response.get("student_id", f"student_{i + 1}")
            results.append(result)

        except Exception as e:
            print(f"Failed to analyze student {i + 1}: {e}")
            results.append({
                "student_id": form_response.get("student_id", f"student_{i + 1}"),
                "error": str(e),
            })

    return results


def print_analysis(analysis: dict):
    """Pretty print the analysis results."""
    print("\n" + "=" * 60)
    print("STUDENT DROPOUT RISK ANALYSIS")
    print("=" * 60)

    if "error" in analysis:
        print(f"\n❌ ERROR: {analysis['error']}")
        return

    print(f"\n📊 DROPOUT PROBABILITY: {analysis['dropout_probability']:.2%}")
    print(f"⚠  RISK LEVEL: {analysis['risk_level']}")

    print("\n🧠 PSYCHOLOGICAL FACTORS:")
    for reason in analysis.get("psychological_reasons", []):
        print(f"  • {reason}")

    print("\n💪 STUDENT STRENGTHS:")
    for strength in analysis.get("student_strengths", []):
        print(f"  • {strength}")

    print("\n🎯 RECOMMENDED INTERVENTIONS:")
    for intervention in analysis.get("recommended_interventions", []):
        print(f"  • {intervention}")

    print("\n" + "=" * 60 + "\n")
