# START HERE — ResumeLens AI

### Part 1 — Prepare
Open PowerShell in this folder and confirm:
```powershell
python --version
pip --version
```

### Part 2 — Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Part 3 — Dependencies
```powershell
pip install -r requirements.txt
```

### Part 4 — Configure
```powershell
Copy-Item .env.example .env
```
Leave `GROQ_API_KEY` blank for Demo Mode. Add your own key for live AI.

### Part 5 — Verify
```powershell
python run_checks.py
```

### Part 6 — Run
```powershell
streamlit run app.py
```

### Part 7 — Demonstrate Task 2
1. Upload a PDF or TXT resume.
2. Verify extracted name/contact/sections.
3. Select target role.
4. Run analysis.
5. Review detected skills.
6. Review potential missing skills.
7. Review transparent deterministic calculations.
8. Review AI feedback.
9. Export the report.
10. Open a saved analysis from the sidebar.

### Accuracy rule
Never treat an AI-generated statement as verified evidence. The app intentionally labels AI feedback as advisory and uses deterministic local calculations for visible percentages.
