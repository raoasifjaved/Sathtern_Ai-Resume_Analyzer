# ResumeLens AI — AI Resume Analyzer

## Task 2 coverage
- Upload Resume (PDF/Text)
- Extract Resume Information
- Analyze Skills
- Suggest Missing Skills
- Generate Basic Feedback Report

## Additional portfolio features
- Target-role selection
- Deterministic, transparent metrics
- SQLite history of saved analyses
- Demo Mode without an API key
- Groq-powered feedback with evidence-aware prompts
- Markdown/TXT/PDF export
- Safe handling of scanned/image-only PDFs (no fake OCR claims)

## Setup — Windows PowerShell
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python run_checks.py
streamlit run app.py
```

## Live AI
Edit `.env`:
```env
GROQ_API_KEY=your_real_key
GROQ_MODEL=openai/gpt-oss-20b
```
Keep `.env` private.

## Accuracy design
The app separates deterministic local metrics from AI-generated feedback.
Skill coverage is calculated locally as:
`matched role skills / role checklist * 100`

"Missing" means a skill was not detected in the uploaded document; it does not prove a person lacks the skill.

## Testing sequence
1. Run `python run_checks.py`.
2. Launch Streamlit.
3. Upload `samples/sample_resume.txt`.
4. Select `Software Engineer`.
5. Run analysis.
6. Verify extracted fields and skills.
7. Check the visible calculation formula.
8. Read AI feedback in live mode or Demo Mode.
9. Export Markdown/TXT/PDF.
10. Upload your own resume and repeat.
