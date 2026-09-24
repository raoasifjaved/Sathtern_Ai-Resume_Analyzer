import re

ROLE_SKILLS = {
    "Software Engineer": ["Python", "Java", "JavaScript", "Git", "SQL", "REST API", "testing", "data structures", "algorithms", "Docker"],
    "AI / ML Engineer": ["Python", "SQL", "Git", "machine learning", "deep learning", "pandas", "NumPy", "scikit-learn", "PyTorch", "TensorFlow"],
    "Data Analyst": ["Python", "SQL", "Excel", "data visualization", "statistics", "pandas", "Power BI", "Tableau"],
    "Data Scientist": ["Python", "SQL", "statistics", "machine learning", "pandas", "NumPy", "scikit-learn", "data visualization"],
    "Web Developer": ["HTML", "CSS", "JavaScript", "Git", "SQL", "REST API", "React", "testing"],
    "Cybersecurity Analyst": ["networking", "Linux", "Python", "SIEM", "incident response", "vulnerability assessment", "firewalls", "security monitoring"],
}

SKILL_ALIASES = {
    "python":["python"],"java":["java"],"javascript":["javascript","js","node.js","nodejs"],"git":["git","github","gitlab"],"sql":["sql","mysql","postgresql","postgres"],
    "rest api":["rest api","restful api","api development"],"testing":["unit testing","integration testing","testing","pytest","junit"],"data structures":["data structures"],"algorithms":["algorithms","algorithm design"],"docker":["docker","containerization"],
    "machine learning":["machine learning","ml"],"deep learning":["deep learning","dl"],"pandas":["pandas"],"numpy":["numpy"],"scikit-learn":["scikit-learn","sklearn"],"pytorch":["pytorch","torch"],"tensorflow":["tensorflow","keras"],
    "excel":["excel","microsoft excel"],"data visualization":["data visualization","data visualisation","visualization"],"statistics":["statistics","statistical analysis"],"power bi":["power bi","powerbi"],"tableau":["tableau"],
    "html":["html","html5"],"css":["css","css3"],"react":["react","react.js","reactjs"],"networking":["networking","computer networks","tcp/ip"],"linux":["linux","ubuntu"],
    "siem":["siem","security information and event management"],"incident response":["incident response","incident handling"],"vulnerability assessment":["vulnerability assessment","vulnerability scanning"],"firewalls":["firewall","firewalls"],"security monitoring":["security monitoring","soc monitoring"]
}

def _contains_skill(text: str, alias: str) -> bool:
    pattern = r"(?<![a-z0-9])" + re.escape(alias.lower()) + r"(?![a-z0-9])"
    return re.search(pattern, text.lower()) is not None

def detect_skills(text: str):
    detected = []
    for canonical, aliases in SKILL_ALIASES.items():
        if any(_contains_skill(text, alias) for alias in aliases):
            detected.append(canonical)
    return sorted(detected)

def role_skill_gap(text: str, role: str):
    detected = set(detect_skills(text))
    checklist = ROLE_SKILLS.get(role, [])
    normalized = {s.lower() for s in detected}
    missing = [s for s in checklist if s.lower() not in normalized]
    matched = [s for s in checklist if s.lower() in normalized]
    return matched, missing, checklist
