# LaunchShield AI

LaunchShield AI is an AI-powered cybersecurity assessment and remediation assistant intended to help independent developers, freelancers, small software agencies, and early-stage businesses understand and address security issues.

## Project status

LaunchShield AI is in early development as an MVP foundation. The current implementation includes a minimal FastAPI backend and a React frontend with a backend health check. Authentication, project management, PostgreSQL persistence, background jobs, security scanners, AI assessment, and the security dashboard are planned functionality and are not yet implemented.

**License:** [MIT License](LICENSE)

## Planned workflow

1. Create a project.
2. Authorize a website or source-code assessment.
3. Run the appropriate security scanners.
4. Normalize scanner findings into a common vulnerability model.
5. Use AI to explain actual findings and recommend remediation.
6. Review findings in a security dashboard.
7. Fix issues and rescan to verify improvements.

LaunchShield AI will never claim that a system is completely secure merely because a scan succeeds. Scan status and coverage must remain clear, including successful, partial, failed, canceled, and untested areas.

## Current technology stack

- Python 3.13
- FastAPI
- Pydantic
- SQLAlchemy
- React
- Vite
- Tailwind CSS 4

## Planned integrations

The following integrations are planned for future development and are not implemented in the current foundation:

- PostgreSQL
- Celery and Redis
- Docker-isolated scanner workers
- OWASP ZAP
- Gitleaks
- OSV-Scanner
- Gemini or another suitable AI provider

## Current repository structure

```text
launchshield-ai/
├── .github/
│   └── copilot-instructions.md
├── backend/
│   ├── app/
│   │   ├── core/
│   │   └── main.py
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── .env.example
│   ├── package.json
│   └── package-lock.json
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

## Local development

### Prerequisites

- Python 3.13
- Node.js and npm
- A virtual environment located at `.venv`

### Backend

From the repository root:

```powershell
.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8000
```

Backend health endpoint:

[http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

Backend API documentation:

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

Backend tests:

```powershell
.venv\Scripts\python.exe -m pytest backend\tests
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Frontend URL:

[http://localhost:5173](http://localhost:5173)

Production frontend build (run from the frontend directory):

```powershell
cd frontend
npm run build
```

The frontend currently uses a Vite development proxy to communicate with the local FastAPI backend. No database or external security service is required for the foundation health check.

## Security principles

- Assess only assets that the user is authorized to test.
- Explicitly verify authorization and domain ownership where required.
- Validate website targets and prevent server-side request forgery.
- Block localhost, private, link-local, reserved, and cloud metadata destinations.
- Revalidate DNS resolutions and redirects.
- Run scanner workloads in isolated, resource-limited containers.
- Restrict scanner outbound network access.
- Protect credentials and secrets through environment variables or an approved secret store.
- Redact secrets from logs, stored unnecessary context, and AI inputs.
- Treat scanner evidence as the source of truth.
- Keep normalized scanner findings separate from AI-generated interpretations.
- Ground AI explanations in actual findings and redacted evidence.
- Never execute uploaded or downloaded source code.
- Never claim a system is completely secure merely because a scan succeeds.

## Environment configuration

The repository includes a root `.env.example` containing planned configuration names. These names are not necessarily consumed by the current application. Add real local values only in an ignored `.env` file or approved secret environment; never commit credentials.
