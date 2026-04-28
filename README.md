# Job-Hunting Agent

A file-driven Python agent for job analysis, resume tailoring, interview preparation, application tracking, and reminder generation.

## Features

- Reads job posters from `input_jobs/`
- Reads resumes from `input_resumes/`
- Reads knowledge-base notes from `input_kb/`
- Generates:
  - `outputs/job_analysis_report.txt`
  - `outputs/skill_gap_report.txt`
  - `outputs/tailored_resume_suggestions.txt`
  - `outputs/interview_questions.txt`
  - `outputs/preparation_plan.txt`
  - `outputs/final_agent_report.txt`
- Maintains:
  - `tracker/applications.csv`
  - `tracker/reminders.txt`

## Project Structure

```text
assignment5/
|-- app.py
|-- requirements.txt
|-- README.md
|-- reflection.md
|-- input_jobs/
|-- input_resumes/
|-- input_kb/
|-- outputs/
|-- tracker/
`-- samples/
```

## Supported File Types

- `.txt`
- `.pdf`
- `.docx`

## How To Run

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Add at least one file in each folder:
   - `input_jobs/`
   - `input_resumes/`
   - `input_kb/`

3. Run the agent:

   ```bash
   python app.py
   ```

## Workflow

1. Read job posters, resumes, and KB files from folders
2. Extract keywords and common technical skills
3. Compare job requirements with resume skills
4. Generate skill-gap and resume-tailoring outputs
5. Create interview questions from job skills and KB notes
6. Create or update the application tracker
7. Generate reminders for interview and follow-up actions

## Notes

- The project includes sample input files so it can run immediately.
- You can replace sample files with your own resume, job posters, and interview notes.
- PDF and DOCX reading are included as an extra feature beyond the minimum assignment requirement.
