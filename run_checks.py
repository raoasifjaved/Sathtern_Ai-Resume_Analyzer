from pathlib import Path
import ast, tempfile
from types import SimpleNamespace
from analyzer import ResumeAnalyzer

BASE = Path(__file__).resolve().parent
PY_FILES = ["app.py","config.py","resume_skills.py","analyzer.py","ai_service.py","database.py","exporters.py","run_checks.py"]
print("[1/6] Checking Python syntax...")
for name in PY_FILES: ast.parse((BASE/name).read_text(encoding="utf-8"), filename=name)
print("      PASS")

sample = """Alex Khan\nalex.khan@example.com\nKarachi, Pakistan\nhttps://github.com/example/alex\n\nSUMMARY\nComputer Science student with Python and SQL experience.\n\nSKILLS\nPython, SQL, Git, REST API, unit testing, Docker\n\nEXPERIENCE\nSoftware Engineering Intern\nBuilt Python REST API endpoints and tests.\n\nEDUCATION\nBS Computer Science\n\nPROJECTS\nStudent Planner using Python and SQLite.\n"""
analyzer = ResumeAnalyzer()
print("[2/6] Checking deterministic skill and information extraction...")
r = analyzer.analyze(sample,"Software Engineer","sample.txt")
assert r["extracted"]["name"] == "Alex Khan"
assert r["extracted"]["email"] == "alex.khan@example.com"
assert "python" in r["skills"]["detected"] and "git" in r["skills"]["detected"]
assert r["deterministic"]["matched_role_skills"] > 0
print("      PASS")

print("[3/6] Checking exact calculation...")
d = r["deterministic"]; expected = round(d["matched_role_skills"] / d["target_role_skill_count"] * 100,1); assert d["skill_coverage_pct"] == expected
print(f"      PASS ({d['matched_role_skills']}/{d['target_role_skill_count']} -> {expected:.1f}%)")

print("[4/6] Checking TXT upload extraction...")
fake = SimpleNamespace(name="resume.txt", getvalue=lambda: b"Hello Resume\nPython")
assert analyzer.extract_text(fake) == "Hello Resume\nPython"
print("      PASS")

print("[5/6] Checking SQLite persistence...")
from database import ResumeDB
with tempfile.TemporaryDirectory() as td:
    db = ResumeDB(str(Path(td)/"test.db")); rid = db.save_resume("sample.txt","Software Engineer",sample,r)
    assert db.get_resume(rid)["filename"] == "sample.txt" and len(db.list_resumes()) == 1
print("      PASS")

print("[6/6] Checking exports...")
from exporters import export_markdown, export_txt, export_pdf
assert "# Resume Analysis Report" in export_markdown(r)
assert "Target role" in export_txt(r)
assert export_pdf(r)[:4] == b"%PDF"
print("      PASS")
print("\nALL CHECKS PASSED")
