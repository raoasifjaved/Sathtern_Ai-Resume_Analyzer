import io
import re
from pathlib import Path
from typing import Any
from resume_skills import detect_skills, role_skill_gap

SECTION_ALIASES = {
    "summary": ["summary", "professional summary", "profile", "objective"],
    "skills": ["skills", "technical skills", "core skills", "competencies"],
    "experience": ["experience", "work experience", "professional experience", "employment"],
    "education": ["education", "academic background", "qualifications"],
    "projects": ["projects", "academic projects", "personal projects"],
    "certifications": ["certifications", "certificates"],
}
SECTION_EXPECTED = ["summary", "skills", "experience", "education", "projects"]
EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
PHONE_RE = re.compile(r"(?<!\d)(?:\+?\d[\d\s().-]{8,}\d)(?!\d)")
URL_RE = re.compile(r"https?://\S+|www\.\S+", re.I)

class ResumeAnalyzer:
    def extract_text(self, uploaded_file) -> str:
        name = Path(uploaded_file.name).name
        raw = uploaded_file.getvalue()
        if name.lower().endswith(".txt"):
            for enc in ("utf-8", "utf-8-sig", "cp1252"):
                try: return raw.decode(enc).replace("\x00", " ").strip()
                except UnicodeDecodeError: pass
            raise ValueError("The TXT file encoding could not be decoded.")
        if name.lower().endswith(".pdf"):
            try:
                from pypdf import PdfReader
            except ImportError as exc:
                raise RuntimeError("pypdf is missing. Run: pip install -r requirements.txt") from exc
            reader = PdfReader(io.BytesIO(raw))
            text = "\n".join((page.extract_text() or "") for page in reader.pages).strip()
            if not text:
                raise ValueError("No selectable text was found. A scanned/image-only PDF needs OCR; this version does not silently pretend OCR succeeded.")
            return text
        raise ValueError("Unsupported file type. Please upload PDF or TXT.")

    def analyze(self, text: str, target_role: str, filename: str) -> dict[str, Any]:
        clean = re.sub(r"[ \t]+", " ", text).strip()
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        lower = text.lower()
        extracted = {
            "name": self._detect_name(lines), "email": self._first_match(EMAIL_RE, text),
            "phone": self._first_match(PHONE_RE, text), "location": self._detect_location(lines),
            "links": sorted(set(URL_RE.findall(text))), "sections_present": self._detect_sections(lower),
            "education": self._evidence_lines(lines, SECTION_ALIASES["education"]),
            "experience": self._evidence_lines(lines, SECTION_ALIASES["experience"]),
            "projects": self._evidence_lines(lines, SECTION_ALIASES["projects"]),
        }
        detected = detect_skills(text)
        matched, missing, checklist = role_skill_gap(text, target_role)
        rows = [{"Section": k.title(), "Detected": "Yes" if k in extracted["sections_present"] else "No"} for k in SECTION_EXPECTED]
        sections_found = sum(1 for r in rows if r["Detected"] == "Yes")
        expected = len(SECTION_EXPECTED)
        matched_n, checklist_n = len(matched), len(checklist)
        coverage = (matched_n / checklist_n * 100) if checklist_n else 0.0
        completeness = (sections_found / expected * 100) if expected else 0.0
        return {
            "filename": filename, "target_role": target_role, "extracted": extracted,
            "skills": {"detected": detected, "matched": matched, "missing": missing},
            "deterministic": {
                "matched_role_skills": matched_n, "target_role_skill_count": checklist_n,
                "skill_coverage_pct": round(coverage, 1), "sections_found": sections_found,
                "sections_expected": expected, "section_completeness_pct": round(completeness, 1),
                "section_details": rows, "character_count": len(clean), "word_count": len(clean.split()),
            }, "ai_feedback": ""
        }

    def demo_feedback(self, result: dict[str, Any]) -> str:
        missing = result["skills"]["missing"]
        d = result["deterministic"]
        lines = ["### Basic Feedback Report (Demo Mode)", "", f"- Target role: **{result['target_role']}**", f"- Detected skills: **{len(result['skills']['detected'])}**", f"- Potential role-skill gaps: **{len(missing)}**", f"- Expected sections detected: **{d['sections_found']}/{d['sections_expected']}**", "", "**Suggested next actions**"]
        if missing:
            lines += ["- Review the missing-skill list and add evidence only for skills you genuinely possess.", f"- Prioritize learning or demonstrating: {', '.join(missing[:6])}."]
        else:
            lines.append("- No gaps were detected against the current role checklist.")
        lines += ["- Add measurable outcomes to experience/project bullets where evidence exists.", "- Keep wording truthful; do not add invented tools, metrics, or responsibilities."]
        return "\n".join(lines)

    def _detect_name(self, lines):
        for line in lines[:6]:
            if EMAIL_RE.search(line) or URL_RE.search(line): continue
            if len(line.split()) <= 5 and not any(ch.isdigit() for ch in line) and not any(w in line.lower() for w in ["resume","curriculum vitae","cv"]):
                return line
        return ""
    def _detect_location(self, lines):
        hints = ["karachi","lahore","islamabad","rawalpindi","peshawar","quetta","pakistan"]
        for line in lines[:20]:
            if any(h in line.lower() for h in hints): return line
        return ""
    def _detect_sections(self, lower_text):
        found = []
        for key, aliases in SECTION_ALIASES.items():
            if any(re.search(rf"(?m)^\s*{re.escape(alias)}\s*:?\s*$", lower_text) for alias in aliases): found.append(key)
        return found
    def _evidence_lines(self, lines, aliases):
        hits, active = [], False
        all_headers = {a.rstrip(":") for vals in SECTION_ALIASES.values() for a in vals}
        for line in lines:
            compact = line.strip().rstrip(":").lower()
            if compact in aliases:
                active = True; continue
            if active:
                if compact in all_headers: break
                if len(line) > 4: hits.append(line)
                if len(hits) >= 6: break
        return hits
    def _first_match(self, pattern, text):
        m = pattern.search(text)
        return m.group(0).strip() if m else ""
