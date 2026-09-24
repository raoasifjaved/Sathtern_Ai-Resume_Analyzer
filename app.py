import json
import streamlit as st
from analyzer import ResumeAnalyzer
from ai_service import AIService
from database import ResumeDB
from exporters import export_markdown, export_txt, export_pdf
from config import settings

st.set_page_config(page_title="ResumeLens AI", page_icon="📄", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
.block-container {padding-top: 1.6rem;}
.hero {padding:1.4rem 1.5rem;border:1px solid rgba(127,127,127,.18);border-radius:20px;margin-bottom:1rem;background:linear-gradient(135deg,rgba(78,70,229,.13),rgba(16,185,129,.10));}
.small-note {color:#666;font-size:.9rem;}
</style>
""", unsafe_allow_html=True)

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""
if "resume_name" not in st.session_state:
    st.session_state.resume_name = ""

analyzer = ResumeAnalyzer()
ai = AIService()
db = ResumeDB(settings.database_path)

with st.sidebar:
    st.title("📄 ResumeLens AI")
    st.caption("Evidence-aware resume analysis workspace")
    st.divider()
    role_choice = st.selectbox("Target role", [
        "Software Engineer", "AI / ML Engineer", "Data Analyst", "Data Scientist",
        "Web Developer", "Cybersecurity Analyst", "Custom"
    ])
    custom_role = st.text_input("Custom target role", placeholder="e.g. Backend Developer") if role_choice == "Custom" else ""
    target_role = custom_role.strip() or role_choice
    st.divider()
    if ai.enabled:
        st.success(f"Connected • {settings.groq_model}")
    else:
        st.info("Demo Mode • deterministic analysis still works")
    st.divider()
    st.subheader("Saved analyses")
    saved = db.list_resumes(limit=10)
    if not saved:
        st.caption("No saved analyses yet.")
    for item in saved:
        label = f"{item['filename']} · {item['target_role']}"
        if st.button(label[:42], key=f"resume_{item['id']}"):
            loaded = db.get_resume(item["id"])
            if loaded:
                st.session_state.resume_name = loaded["filename"]
                st.session_state.resume_text = loaded["raw_text"]
                st.session_state.analysis_result = json.loads(loaded["analysis_json"])
                st.rerun()
    st.divider()
    st.caption("Local extraction runs first. Live AI mode sends resume text to the configured AI provider.")

st.markdown("""
<div class="hero">
<h1>📄 ResumeLens AI</h1>
<p>Upload a PDF or text resume. Extract the evidence, map skills to a target role,
identify gaps, and generate a practical feedback report.</p>
</div>
""", unsafe_allow_html=True)

left, right = st.columns([1.05, 0.95])

with left:
    st.subheader("1. Upload Resume")
    uploaded = st.file_uploader("PDF or TXT file", type=["pdf", "txt"])
    if uploaded is not None:
        if uploaded.size > settings.max_upload_mb * 1024 * 1024:
            st.error(f"File is too large. Maximum size is {settings.max_upload_mb} MB.")
        else:
            try:
                text = analyzer.extract_text(uploaded)
                st.session_state.resume_text = text
                st.session_state.resume_name = uploaded.name
                st.success(f"Extracted {len(text):,} characters from {uploaded.name}.")
            except Exception as exc:
                st.error(f"Could not extract the resume: {exc}")
    if st.session_state.resume_text:
        st.caption(f"Loaded: **{st.session_state.resume_name}**")
        st.text_area("Extracted text preview", st.session_state.resume_text[:3500], height=320)

with right:
    st.subheader("2. Analyze")
    if not st.session_state.resume_text:
        st.info("Upload a resume to begin.")
    else:
        st.write(f"Target role: **{target_role}**")
        if st.button("🔎 Run Resume Analysis", type="primary", use_container_width=True):
            with st.spinner("Extracting evidence and calculating deterministic metrics..."):
                result = analyzer.analyze(st.session_state.resume_text, target_role, st.session_state.resume_name)
            if ai.enabled:
                with st.spinner("Generating AI feedback report..."):
                    try:
                        result["ai_feedback"] = ai.generate_feedback(
                            st.session_state.resume_text,
                            result["extracted"],
                            result["deterministic"],
                            target_role,
                        )
                    except Exception as exc:
                        result["ai_feedback"] = analyzer.demo_feedback(result)
                        st.warning(f"AI feedback failed safely; showing deterministic/demo feedback instead. Reason: {exc}")
            else:
                result["ai_feedback"] = analyzer.demo_feedback(result)
            st.session_state.analysis_result = result
            db.save_resume(st.session_state.resume_name, target_role, st.session_state.resume_text, result)
            st.success("Analysis complete and saved.")

if st.session_state.analysis_result:
    result = st.session_state.analysis_result
    d = result["deterministic"]
    st.divider()
    st.subheader("3. Resume Analysis Dashboard")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Skill coverage", f"{d['skill_coverage_pct']:.1f}%")
    c2.metric("Sections found", f"{d['sections_found']}/{d['sections_expected']}")
    c3.metric("Skills detected", str(len(result["skills"]["detected"])))
    c4.metric("Role skills not detected", str(len(result["skills"]["missing"])))

    tabs = st.tabs(["📌 Extracted Information", "🧠 Skills", "📈 Deterministic Metrics", "💡 AI Feedback", "📦 Export"])
    with tabs[0]:
        e = result["extracted"]
        a,b = st.columns(2)
        with a:
            st.write("**Name**", e.get("name") or "Not detected")
            st.write("**Email**", e.get("email") or "Not detected")
            st.write("**Phone**", e.get("phone") or "Not detected")
        with b:
            st.write("**Location**", e.get("location") or "Not detected")
            st.write("**Links**", ", ".join(e.get("links", [])) or "Not detected")
            st.write("**Sections**", ", ".join(e.get("sections_present", [])) or "Not detected")
        st.markdown("**Education evidence**")
        for item in e.get("education", []): st.write(f"- {item}")
        st.markdown("**Experience evidence**")
        for item in e.get("experience", []): st.write(f"- {item}")
        st.markdown("**Project evidence**")
        for item in e.get("projects", []): st.write(f"- {item}")
    with tabs[1]:
        st.markdown("**Detected skills**")
        st.write(", ".join(result["skills"]["detected"]) or "No skills detected from the current taxonomy.")
        st.markdown("**Potentially missing skills for the selected target role**")
        st.write(", ".join(result["skills"]["missing"]) or "No missing skills from the selected role checklist.")
        st.caption("Missing means the skill was not detected in the uploaded text. It does not prove the applicant lacks that skill.")
    with tabs[2]:
        st.write("These metrics are calculated locally from extracted evidence.")
        st.markdown(f"**Skill coverage** = matched role skills ÷ role checklist × 100 = {d['matched_role_skills']} ÷ {d['target_role_skill_count']} × 100 = **{d['skill_coverage_pct']:.1f}%**")
        st.markdown(f"**Section completeness** = sections found ÷ expected sections × 100 = {d['sections_found']} ÷ {d['sections_expected']} × 100 = **{d['section_completeness_pct']:.1f}%**")
        st.dataframe(d["section_details"], use_container_width=True, hide_index=True)
        st.warning("These are document-coverage measures, not hiring scores and not predictions of job performance.")
    with tabs[3]:
        st.caption("AI-generated feedback is advisory. Verify factual claims and technical suggestions before using them.")
        st.markdown(result["ai_feedback"])
    with tabs[4]:
        st.download_button("⬇ Download Markdown", export_markdown(result), "resume_analysis_report.md", "text/markdown", use_container_width=True)
        st.download_button("⬇ Download TXT", export_txt(result), "resume_analysis_report.txt", "text/plain", use_container_width=True)
        st.download_button("⬇ Download PDF", export_pdf(result), "resume_analysis_report.pdf", "application/pdf", use_container_width=True)

st.divider()
st.caption("ResumeLens AI • local extraction + optional Groq feedback • AI output should be verified before use.")
