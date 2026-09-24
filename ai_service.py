from config import settings

SYSTEM_PROMPT = """
You are ResumeLens AI, an evidence-aware resume feedback assistant.
Use only information present in the supplied resume and deterministic metrics.
Do not invent skills, employers, degrees, dates, metrics, achievements, certifications, or tools.
A skill not detected is not proof that the person lacks it.
Never provide hiring probabilities, hiring scores, or claims about future job outcomes.
Do not claim code or tests were run unless execution evidence is supplied.
Keep numerical statements consistent with the supplied metrics.
Clearly label ambiguity and assumptions.
"""

class AIService:
    def __init__(self): self.enabled = bool(settings.groq_api_key)
    def generate_feedback(self, resume_text, extracted, deterministic, target_role):
        if not self.enabled: return "AI mode is disabled."
        try:
            from groq import Groq
        except ImportError as exc:
            raise RuntimeError("The groq package is missing. Run: pip install -r requirements.txt") from exc
        client = Groq(api_key=settings.groq_api_key, timeout=settings.groq_timeout)
        prompt = f"""
Target role: {target_role}
Deterministic metrics: {deterministic}
Extracted resume fields: {extracted}
Resume text:\n{resume_text[:settings.max_resume_chars]}

Write a concise feedback report with exactly these headings:
## Summary
## Strengths visible in the document
## Potential missing skills or evidence
## Resume improvements
## Suggested learning priorities
## Verification notes
Use only evidence from the input. Missing evidence is not proof of absence.
"""
        response = client.chat.completions.create(
            model=settings.groq_model,
            messages=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":prompt}],
            temperature=0.2,
            max_completion_tokens=1600,
        )
        content = response.choices[0].message.content
        return content.strip() if content else "The AI provider returned an empty response."
