# Reflection

## Student Information

- Name: Hamyal
- Roll Number: 22F-3184
- Section: BSAI-8B

## What I Built

I built a file-driven Job-Hunting Agent in Python that reads job posters, resumes, and knowledge-base files from structured folders. The agent analyzes job requirements, compares them with resume skills, generates interview questions, creates a preparation plan, and maintains an application tracker with reminders.

## What Was Implemented

- Folder-based file reading
- Job analysis report
- Resume skill extraction
- Skill-gap report
- Tailored resume suggestions
- Interview question generation from KB content
- Application tracker in CSV format
- Reminder generation in text format
- Optional PDF and DOCX support

## Testing Done

I tested the project by adding sample files in all required input folders and running `python app.py`. The script completed successfully and produced all expected files in `outputs/` and `tracker/`.

## Improvements Added

Beyond the minimum requirements, I added:

- PDF reading support
- DOCX reading support
- A preparation plan output
- Multi-file folder loading
- Automatic tracker creation from job inputs

## What I Learned

This activity helped me understand how to design a simple AI-style workflow using folders as the environment, generated files as memory/output, and structured processing steps to simulate agent behavior.
