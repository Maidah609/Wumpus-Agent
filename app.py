import csv
import re
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    from docx import Document
except ImportError:
    Document = None


BASE_DIR = Path(__file__).resolve().parent
INPUT_JOBS_DIR = BASE_DIR / "input_jobs"
INPUT_RESUMES_DIR = BASE_DIR / "input_resumes"
INPUT_KB_DIR = BASE_DIR / "input_kb"
OUTPUTS_DIR = BASE_DIR / "outputs"
TRACKER_DIR = BASE_DIR / "tracker"
SAMPLES_DIR = BASE_DIR / "samples"

TRACKER_HEADERS = [
    "application_id",
    "company",
    "role",
    "source",
    "status",
    "applied_date",
    "interview_date",
    "follow_up_date",
    "next_action",
    "notes",
]

KNOWN_SKILLS = {
    "python",
    "sql",
    "java",
    "javascript",
    "typescript",
    "html",
    "css",
    "react",
    "node.js",
    "node",
    "django",
    "flask",
    "fastapi",
    "git",
    "github",
    "docker",
    "kubernetes",
    "linux",
    "machine learning",
    "deep learning",
    "nlp",
    "computer vision",
    "data analysis",
    "data structures",
    "algorithms",
    "pandas",
    "numpy",
    "scikit-learn",
    "tensorflow",
    "pytorch",
    "opencv",
    "mysql",
    "postgresql",
    "mongodb",
    "rest api",
    "api",
    "streamlit",
    "communication",
    "problem solving",
    "teamwork",
    "oop",
    "object oriented programming",
    "excel",
}

ROLE_HINTS = [
    "intern",
    "engineer",
    "developer",
    "analyst",
    "scientist",
    "associate",
]

def ensure_folders() -> None:
    for folder in [
        INPUT_JOBS_DIR,
        INPUT_RESUMES_DIR,
        INPUT_KB_DIR,
        OUTPUTS_DIR,
        TRACKER_DIR,
        SAMPLES_DIR,
    ]:
        folder.mkdir(parents=True, exist_ok=True)


def read_txt_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_pdf_file(path: Path) -> str:
    if PdfReader is None:
        return ""
    reader = PdfReader(str(path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def read_docx_file(path: Path) -> str:
    if Document is None:
        return ""
    doc = Document(str(path))
    return "\n".join(paragraph.text for paragraph in doc.paragraphs)


def read_supported_file(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".txt":
        return read_txt_file(path)
    if suffix == ".pdf":
        return read_pdf_file(path)
    if suffix == ".docx":
        return read_docx_file(path)
    return ""


def load_folder_text(folder: Path) -> tuple[str, list[dict[str, str]]]:
    items = []
    combined_parts = []
    for path in sorted(folder.iterdir()):
        if not path.is_file():
            continue
        text = read_supported_file(path).strip()
        if not text:
            continue
        items.append({"name": path.name, "text": text})
        combined_parts.append(f"\n## {path.name}\n{text}\n")
    return "\n".join(combined_parts).strip(), items


def normalize_text(text: str) -> str:
    lowered = text.lower()
    lowered = lowered.replace("node js", "node.js")
    lowered = lowered.replace("nodejs", "node.js")
    lowered = lowered.replace("restful api", "rest api")
    return lowered


def extract_keywords(text: str) -> list[str]:
    normalized = normalize_text(text)
    found = []
    for skill in sorted(KNOWN_SKILLS, key=len, reverse=True):
        pattern = r"(?<![a-z0-9])" + re.escape(skill) + r"(?![a-z0-9])"
        if re.search(pattern, normalized):
            found.append(skill)
    return sorted(found)


def extract_top_terms(text: str, limit: int = 12) -> list[tuple[str, int]]:
    tokens = re.findall(r"[a-zA-Z][a-zA-Z\+\#\.]{2,}", text.lower())
    stop_words = {
        "the",
        "and",
        "with",
        "for",
        "you",
        "your",
        "are",
        "our",
        "will",
        "this",
        "that",
        "from",
        "have",
        "has",
        "job",
        "role",
        "work",
        "team",
        "using",
        "into",
        "their",
        "they",
        "who",
        "all",
        "but",
        "can",
        "not",
        "one",
        "two",
        "any",
        "etc",
    }
    filtered = [token for token in tokens if token not in stop_words]
    return Counter(filtered).most_common(limit)


def detect_role(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in lines[:10]:
        lowered = line.lower()
        if any(hint in lowered for hint in ROLE_HINTS):
            return re.sub(r"^(role|position)\s*:\s*", "", line, flags=re.IGNORECASE).strip()
    return "Role not clearly identified"


def detect_company(text: str, fallback_name: str) -> str:
    patterns = [
        r"company[:\-]\s*(.+)",
        r"organization[:\-]\s*(.+)",
        r"employer[:\-]\s*(.+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip()
    stem = Path(fallback_name).stem.replace("_", " ").replace("-", " ")
    return stem.title()


def compare_skills(job_skills: list[str], resume_skills: list[str]) -> tuple[list[str], list[str], int]:
    job_set = set(job_skills)
    resume_set = set(resume_skills)
    matched = sorted(job_set & resume_set)
    missing = sorted(job_set - resume_set)
    score = int((len(matched) / len(job_set)) * 100) if job_set else 0
    return matched, missing, score


def generate_job_analysis_report(job_items: list[dict[str, str]]) -> str:
    lines = ["Job Analysis Report", "===================", ""]
    for index, item in enumerate(job_items, start=1):
        text = item["text"]
        role = detect_role(text)
        company = detect_company(text, item["name"])
        skills = extract_keywords(text)
        top_terms = extract_top_terms(text)

        lines.append(f"Job #{index}: {item['name']}")
        lines.append(f"Company: {company}")
        lines.append(f"Detected role: {role}")
        lines.append(f"Detected skills: {', '.join(skills) if skills else 'No known skills found'}")
        lines.append("Top terms:")
        for term, count in top_terms:
            lines.append(f"- {term}: {count}")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def generate_skill_gap_report(
    selected_job_name: str,
    job_skills: list[str],
    resume_skills: list[str],
    matched: list[str],
    missing: list[str],
    score: int,
) -> str:
    lines = [
        "Skill Gap Report",
        "================",
        "",
        f"Selected job: {selected_job_name}",
        f"Match score: {score}%",
        f"Job skills found: {', '.join(job_skills) if job_skills else 'None'}",
        f"Resume skills found: {', '.join(resume_skills) if resume_skills else 'None'}",
        "",
        "Matched skills:",
    ]
    if matched:
        lines.extend(f"- {skill}" for skill in matched)
    else:
        lines.append("- No strong matches found")

    lines.extend(["", "Missing or weak areas:"])
    if missing:
        lines.extend(f"- {skill}" for skill in missing)
    else:
        lines.append("- No major missing skills detected")

    return "\n".join(lines).strip() + "\n"


def generate_resume_suggestions(job_skills: list[str], matched: list[str], missing: list[str]) -> str:
    lines = [
        "Tailored Resume Suggestions",
        "===========================",
        "",
        "Suggested summary updates:",
        "- Add a short summary focused on the target role and your strongest technical skills.",
        "- Highlight relevant academic, freelance, or personal projects before unrelated details.",
        "- Use action verbs and measurable outcomes wherever possible.",
        "",
        "Suggested bullets to emphasize:",
    ]

    for skill in matched[:5]:
        lines.append(f"- Add or strengthen a project bullet that proves hands-on work with {skill}.")

    if not matched:
        lines.append("- Add your strongest technical project with clear technologies and outcomes.")

    lines.extend(["", "Skills to improve before applying/interview:"])
    if missing:
        for skill in missing:
            lines.append(f"- Study or practice {skill} and prepare one example showing how you can learn or apply it.")
    else:
        lines.append("- Focus on polishing wording and preparing examples for your current strengths.")

    lines.extend(["", "Resume tailoring note:", f"- Mirror the job wording for these key skills: {', '.join(job_skills[:8]) if job_skills else 'No major keywords detected'}"])
    return "\n".join(lines).strip() + "\n"


def generate_interview_questions(job_skills: list[str], kb_text: str) -> str:
    lines = [
        "Interview Questions",
        "===================",
        "",
        "Technical questions based on the selected job:",
    ]
    for skill in job_skills[:10]:
        lines.append(f"- Explain your understanding of {skill}.")
        lines.append(f"- Describe a project, assignment, or task where you used {skill}.")

    lines.extend(
        [
            "",
            "HR and behavioral questions:",
            "- Tell me about yourself.",
            "- Why are you interested in this role?",
            "- What project are you most proud of and why?",
            "- Describe a time you learned a new skill quickly.",
            "- How do you handle deadlines and teamwork?",
        ]
    )

    kb_lines = [line.strip("- ").strip() for line in kb_text.splitlines() if line.strip()]
    lines.extend(["", "Questions inspired by the knowledge base:"])
    if kb_lines:
        for line in kb_lines[:10]:
            lines.append(f"- In an interview, how would you explain this concept: {line}?")
    else:
        lines.append("- Add more KB notes to generate topic-specific questions.")

    return "\n".join(lines).strip() + "\n"


def generate_preparation_plan(job_skills: list[str], missing: list[str]) -> str:
    lines = [
        "Preparation Plan",
        "================",
        "",
        "Day 1:",
        "- Review the selected job description and identify the top required skills.",
        "- Update resume summary and project bullets.",
        "",
        "Day 2:",
        f"- Revise these priority skills: {', '.join(job_skills[:5]) if job_skills else 'core job skills'}.",
        "- Practice explaining at least two projects clearly.",
        "",
        "Day 3:",
        "- Prepare HR answers and mock interview responses.",
        "- Review GitHub/portfolio links and make sure they are clean and current.",
        "",
        "Extra focus areas:",
    ]
    if missing:
        lines.extend(f"- Build quick revision notes for {skill}." for skill in missing[:5])
    else:
        lines.append("- Focus on confidence, clarity, and concise project explanations.")
    return "\n".join(lines).strip() + "\n"


def save_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def create_or_update_tracker(job_items: list[dict[str, str]]) -> Path:
    tracker_path = TRACKER_DIR / "applications.csv"
    today = date.today().isoformat()

    new_rows = []
    for index, job in enumerate(job_items, start=1):
        app_id = f"APP-{index:03d}"
        company = detect_company(job["text"], job["name"])
        role = detect_role(job["text"])
        status = "Interview Scheduled" if index == 1 else "Not Applied"
        interview_date = ((date.today() + timedelta(days=3)).isoformat() if index == 1 else "")
        follow_up_date = ((date.today() + timedelta(days=6)).isoformat() if index == 1 else "")
        row = {
            "application_id": app_id,
            "company": company,
            "role": role,
            "source": "Input Job Poster",
            "status": status,
            "applied_date": today if status != "Not Applied" else "",
            "interview_date": interview_date,
            "follow_up_date": follow_up_date,
            "next_action": "Prepare interview questions and revise projects" if status == "Interview Scheduled" else "Tailor resume and apply",
            "notes": "Generated by the file-driven agent",
        }
        new_rows.append(row)

    with tracker_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=TRACKER_HEADERS)
        writer.writeheader()
        writer.writerows(new_rows)

    return tracker_path


def parse_date(value: str) -> date | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def generate_reminders(tracker_path: Path) -> str:
    lines = ["Application Reminders", "=====================", ""]
    today = date.today()

    with tracker_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    if not rows:
        return "Application Reminders\n=====================\n\nNo application records found.\n"

    for row in rows:
        app_id = row.get("application_id", "")
        company = row.get("company", "")
        role = row.get("role", "")
        status = row.get("status", "")
        interview_date = parse_date(row.get("interview_date", ""))
        follow_up_date = parse_date(row.get("follow_up_date", ""))
        next_action = row.get("next_action", "")

        if status.lower() == "interview scheduled" and interview_date:
            urgency = "overdue" if interview_date < today else "upcoming"
            lines.append(
                f"- {app_id}: Interview for {role} at {company} on {interview_date.isoformat()} ({urgency}). Next action: {next_action}"
            )
        elif status.lower() == "applied" and follow_up_date:
            urgency = "due" if follow_up_date <= today else "planned"
            lines.append(
                f"- {app_id}: Follow up with {company} for {role} on {follow_up_date.isoformat()} ({urgency})."
            )
        elif status.lower() == "not applied":
            lines.append(f"- {app_id}: Resume still needs tailoring for {role} at {company}.")
        else:
            lines.append(f"- {app_id}: Review application status for {role} at {company}.")

    return "\n".join(lines).strip() + "\n"


def pick_primary_job(job_items: list[dict[str, str]]) -> dict[str, str]:
    return job_items[0]


def run_agent() -> None:
    ensure_folders()

    jobs_text, job_items = load_folder_text(INPUT_JOBS_DIR)
    resumes_text, resume_items = load_folder_text(INPUT_RESUMES_DIR)
    kb_text, kb_items = load_folder_text(INPUT_KB_DIR)

    if not job_items or not resume_items or not kb_items:
        print("Please add at least one supported file to input_jobs, input_resumes, and input_kb.")
        return

    primary_job = pick_primary_job(job_items)
    primary_resume = resume_items[0]

    job_skills = extract_keywords(primary_job["text"])
    resume_skills = extract_keywords(primary_resume["text"])
    matched, missing, score = compare_skills(job_skills, resume_skills)

    job_analysis_report = generate_job_analysis_report(job_items)
    skill_gap_report = generate_skill_gap_report(primary_job["name"], job_skills, resume_skills, matched, missing, score)
    resume_suggestions = generate_resume_suggestions(job_skills, matched, missing)
    interview_questions = generate_interview_questions(job_skills, kb_text)
    preparation_plan = generate_preparation_plan(job_skills, missing)

    tracker_path = create_or_update_tracker(job_items)
    reminders = generate_reminders(tracker_path)

    final_report = "\n".join(
        [
            "CareerPrep Job-Hunting Agent Report",
            "===================================",
            f"Generated on: {datetime.now().isoformat(timespec='seconds')}",
            f"Job files read: {len(job_items)}",
            f"Resume files read: {len(resume_items)}",
            f"KB files read: {len(kb_items)}",
            f"Primary job selected: {primary_job['name']}",
            f"Match score: {score}%",
            "",
            job_analysis_report.strip(),
            "",
            skill_gap_report.strip(),
            "",
            resume_suggestions.strip(),
            "",
            interview_questions.strip(),
            "",
            preparation_plan.strip(),
            "",
            reminders.strip(),
            "",
        ]
    )

    save_text(OUTPUTS_DIR / "job_analysis_report.txt", job_analysis_report)
    save_text(OUTPUTS_DIR / "skill_gap_report.txt", skill_gap_report)
    save_text(OUTPUTS_DIR / "tailored_resume_suggestions.txt", resume_suggestions)
    save_text(OUTPUTS_DIR / "interview_questions.txt", interview_questions)
    save_text(OUTPUTS_DIR / "preparation_plan.txt", preparation_plan)
    save_text(OUTPUTS_DIR / "final_agent_report.txt", final_report)
    save_text(TRACKER_DIR / "reminders.txt", reminders)

    print("Agent completed successfully.")
    print(f"Job files read: {len(job_items)}")
    print(f"Resume files read: {len(resume_items)}")
    print(f"KB files read: {len(kb_items)}")
    print(f"Match score: {score}%")
    print("Generated outputs saved in outputs/ and tracker/.")


if __name__ == "__main__":
    run_agent()
