from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def export_markdown(result):
    d,e,s = result["deterministic"], result["extracted"], result["skills"]
    return "\n".join([
        f"# Resume Analysis Report — {result['filename']}", "", f"**Target role:** {result['target_role']}", "",
        "## Deterministic Metrics", f"- Skill coverage: {d['skill_coverage_pct']:.1f}%", f"- Sections detected: {d['sections_found']}/{d['sections_expected']}", f"- Word count: {d['word_count']}", "",
        "## Extracted Information", f"- Name: {e.get('name') or 'Not detected'}", f"- Email: {e.get('email') or 'Not detected'}", f"- Phone: {e.get('phone') or 'Not detected'}", f"- Location: {e.get('location') or 'Not detected'}", "",
        "## Skills Detected", ", ".join(s["detected"]) if s["detected"] else "None detected", "",
        "## Potentially Missing Skills", ", ".join(s["missing"]) if s["missing"] else "None detected from the role checklist", "",
        "## AI Feedback", result.get("ai_feedback", ""), "", "> Note: AI feedback is advisory. Missing evidence is not proof that a person lacks a skill."
    ])

def export_txt(result): return export_markdown(result).replace("**", "").replace("# ", "")

def export_pdf(result):
    buf = BytesIO(); doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=40,leftMargin=40,topMargin=40,bottomMargin=40); styles = getSampleStyleSheet(); story=[]
    for block in export_markdown(result).split("\n"):
        if not block.strip(): story.append(Spacer(1,8)); continue
        safe = block.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
        if block.startswith("# "): story.append(Paragraph(safe[2:], styles["Title"]))
        elif block.startswith("## "): story.append(Paragraph(safe[3:], styles["Heading2"]))
        else: story.append(Paragraph(safe, styles["BodyText"]))
    doc.build(story); return buf.getvalue()
