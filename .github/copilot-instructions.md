# LaunchShield AI — Copilot Project Instructions

## 1. Project Overview and Objectives

LaunchShield AI is an AI-powered cybersecurity assessment and remediation assistant for independent developers, freelancers, small software agencies, early-stage startups, and small online businesses.

The platform must:

- Identify security vulnerabilities from real scanner evidence.
- Explain why findings matter in understandable language.
- Assign or preserve scanner-derived severity where available.
- Recommend actionable remediation steps.
- Support rescanning and before-and-after comparison.
- Help project users ask project-specific questions through the Shield Assistant.
- Never claim that an application is completely secure merely because a scan completed or passed.
- Clearly distinguish successful, partial, failed, canceled, and untested scan coverage.

The primary goal is a reliable, secure, genuinely working hackathon MVP. Wide feature coverage is less important than end-to-end correctness and security.

## 2. Python-First Technology Stack

Python is the primary programming language.

Approved technologies:

- Backend: FastAPI, Pydantic, SQLAlchemy
- Database: PostgreSQL
- Background processing: Celery and Redis
- Frontend: React, Vite, and Tailwind CSS
- Website scanner: OWASP ZAP
- Source secret scanner: Gitleaks
- Dependency scanner: OSV-Scanner
- Isolation: Docker
- AI: Gemini API or a suitable provider abstraction
- Testing: Pytest and Keploy
- Deployment: Render or an equivalent platform
- CI/CD: GitHub Actions when needed

JavaScript should be used only where required for the React frontend. Do not introduce organizations, teams, n8n, Sentry, additional databases, alternate frameworks, or other integrations merely for convenience unless a later approved phase requires them.

All API keys and credentials must come from environment variables or a managed secret store. Never hardcode or log secrets.

## 3. Approved System Architecture

Use this architecture:

```text
React + Vite + Tailwind
          |
       HTTPS
          |
FastAPI REST API
          |
  +-------+--------+
  |                |
PostgreSQL        Redis
                   |
                 Celery
                   |
          Scanner worker containers
          +--------+--------+
          |        |        |
          ZAP    Gitleaks   OSV
```

AI workflow:

```text
Normalized scanner findings
  -> AI interpretation service
  -> validated, stored explanations
  -> dashboard and project Shield Assistant
```

Redis is the Celery broker and a short-lived coordination/cache layer. Redis must not be treated as the source of truth.

PostgreSQL is the durable source of truth for users, projects, authorization records, scan state, findings, evidence, AI interpretations, chat conversations, and comparison history.

## 4. Backend Architecture and Module Responsibilities

The backend should remain modular. API routes should coordinate requests and responses; services should implement business rules; repositories or clearly isolated database operations should handle persistence; scanner adapters should translate scanner-native data; and worker tasks should execute asynchronous jobs.

Expected module responsibilities:

- `api/routes/`: FastAPI route handlers, authentication dependencies, request/response schemas, and HTTP status handling.
- `core/`: configuration, security, logging, application constants, and shared dependencies.
- `db/`: SQLAlchemy setup, sessions, base models, and migrations.
- `models/`: SQLAlchemy entities.
- `schemas/`: Pydantic validation and API response models.
- `repositories/`: ownership-checked database access where this abstraction is used.
- `services/authorization/`: target authorization and URL safety validation.
- `services/normalization/`: common finding models and scanner-result normalization.
- `services/ai/`: evidence-grounded AI interpretation and provider integration.
- `integrations/zap/`: ZAP invocation and native-result parsing.
- `integrations/gitleaks/`: Gitleaks invocation and native-result parsing.
- `integrations/osv/`: OSV invocation and native-result parsing.
- `workers/`: Celery application configuration and idempotent task implementations.

Do not place scanner parsing, AI logic, authorization checks, or ownership enforcement directly inside large route handlers.

Use environment-based configuration, structured logging, bounded retries, clear exception handling, and cancellable or time-bounded operations where relevant.

The exact authentication mechanism is a Phase 2 implementation decision. Any secure mechanism may be used when that phase is approved, but passwords must be hashed and every protected endpoint must enforce user-level data isolation.

## 5. Database Ownership and Relationships

The required entities and relationships are:

- `User` owns many `Project` records.
- `Project` has many `AuthorizationRecord`, `Scan`, and `ChatConversation` records.
- `Scan` belongs to a `Project` and is initiated by a `User`.
- `Scan` has many `Finding`, `FindingEvidence`, `ScanArtifact`, and `AIInterpretation` records.
- `Finding` belongs to a `Scan` and may have many `FindingEvidence` and `AIInterpretation` records.
- `ChatConversation` belongs to a `Project` and may have many `ChatMessage` records.
- `ChatMessage` belongs to a `ChatConversation` and is associated with the authenticated user.

Every project-scoped, scan-scoped, finding-scoped, evidence-scoped, artifact-scoped, interpretation-scoped, and conversation-scoped query must verify the authenticated user's project ownership.

`User`, `Project`, `AuthorizationRecord`, `Scan`, `Finding`, `FindingEvidence`, `ScanArtifact`, `AIInterpretation`, `ChatConversation`, and `ChatMessage` are the conceptual entities. Additional entities may be added only when a later approved phase requires them.

Scanner-native evidence and AI-generated content must remain separate:

- `Finding` contains normalized scanner-derived fields.
- `FindingEvidence` contains redacted evidence and scanner-native metadata.
- `ScanArtifact` contains bounded, redacted artifact references.
- `AIInterpretation` contains model-generated explanation and remediation content.
- `ChatMessage` contains conversation content and references to retrieved project findings.

An AI interpretation must never overwrite or replace scanner evidence.

## 6. Scanner Integration Requirements

### OWASP ZAP

- Scan only validated and authorized HTTP or HTTPS targets.
- Prefer passive or baseline scanning for the MVP.
- Active scanning must remain disabled or tightly configured until mature authorization verification exists.
- Parse alerts into normalized findings.
- Preserve native ZAP identifiers and relevant redacted evidence.
- Apply target scope, depth, port, response-size, request-count, and timeout limits.
- Revalidate every redirect destination.

### Gitleaks

- Accept only bounded source archives or read-only repository access.
- Never execute repository or uploaded source code.
- Redact secret values during ingestion.
- Store secret type, location, fingerprint, and only safe context in findings/evidence.
- Never place raw secret values in logs or AI context.
- Remove temporary source and artifact directories after processing.

### OSV-Scanner

- Accept lockfiles or supported dependency manifests only; do not execute application code.
- Parse package name, affected version, advisory identity, fixed version/range, and available evidence.
- Preserve native advisory metadata and severity information when supplied.
- Do not infer a vulnerability when dependency evidence is unavailable.
- Bound manifest and result sizes.

### Normalized Findings

Every normalized finding should preserve:

- Stable fingerprint
- Scanner source
- Native identifier
- Title
- Severity
- Confidence
- Category or CWE/CVE where available
- Affected component, URL, package, or location
- Redacted evidence
- Remediation summary
- First/last observed timestamps
- Resolution state

The fingerprint should combine relevant stable source, rule/advisory identity, and normalized location to support new/persistent/resolved comparisons.

## 7. Scanner Worker Isolation and Restricted Networking

Scanner containers must:

- Run as non-root.
- Use isolated Docker networks.
- Have read-only filesystems where practical.
- Allow writes only in explicitly temporary, bounded directories.
- Receive no direct database or application credential access.
- Receive only target, project/scan identifiers, and permitted bounded options.
- Never accept arbitrary shell commands or executable code.
- Apply CPU, memory, process, file-size, and execution-time limits.
- Clean temporary files and artifacts.
- Use a restricted outbound proxy or equivalent network enforcement mechanism.

The proxy or equivalent must:

- Block direct unrestricted scanner egress.
- Accept traffic only from the isolated scanner network.
- Resolve destinations and inspect final IP addresses.
- Reject localhost, loopback, private, link-local, multicast, reserved, and cloud metadata destinations.
- Limit ports to required public HTTP/HTTPS ports.
- Validate every redirect destination and target scope.
- Revalidate DNS at dispatch and immediately before connection.
- Detect or reject DNS rebinding.
- Bound requests, responses, and total execution time.
- Avoid logging credentials or sensitive response bodies.

A direct allowlist is not sufficient. DNS and redirects must be checked again at connection time.

## 8. Authorization, Domain Verification, URL Validation, and SSRF Protection

These requirements are distinct:

1. **User authorization assertion:** The authenticated user explicitly confirms that they are authorized to assess the target. Authentication alone does not prove authorization.
2. **Domain ownership verification:** A future target should demonstrate control with a suitable challenge. The simple controlled demonstration may use a preconfigured demo domain, a DNS TXT record, or a hosted validation endpoint.
3. **URL validation:** The backend must validate absolute HTTP/HTTPS URLs, reject credentials and unsupported schemes, and parse/normalize hosts and ports safely.
4. **Network-level enforcement:** The scanner worker and restricted proxy independently deny unsafe destinations, even after successful authorization and URL validation.

For the controlled hackathon MVP:

- Require explicit authorization confirmation.
- Prefer a preconfigured public demonstration website or DNS TXT verification.
- Allow only the intended target scope.
- Apply all URL, DNS, redirect, proxy, private-network, and metadata protections.
- Do not require a complex interactive third-party ownership platform unless a later phase explicitly adopts it.

The backend must block and recheck:

- localhost and loopback addresses
- RFC1918 private addresses
- link-local addresses
- reserved and multicast ranges
- cloud metadata endpoints
- credentials embedded in URLs
- non-HTTP/HTTPS schemes
- rebinding or redirect changes outside the authorized scope

No URL is safe because an authenticated user supplied it.

## 9. AI Evidence-Grounding Requirements

AI interpretation must be grounded in actual normalized findings and redacted evidence.

The AI service must:

- Receive only allowlisted finding fields and safe evidence context.
- Preserve and cite the scanner source.
- Produce structured plain-language explanation, impact, remediation steps, verification guidance, and limitations.
- Refuse to invent missing evidence or claim that a weakness exists without scanner support.
- Validate output through Pydantic or equivalent schemas.
- Store interpretations separately from findings and evidence.
- Generate an interpretation only from the finding currently being interpreted.
- Handle provider failures without changing scanner status or inventing results.
- Never expose raw Gitleaks secrets or unrelated project data.
- Never claim resolution or complete security.

A remediated finding's resolution status must come from a comparison of subsequent scan evidence, not from an AI response.

## 10. Shield Assistant Data Access Restrictions

The Shield Assistant is project-specific and must:

- Use only project-owned findings and selected scan summaries.
- Enforce project ownership before retrieval.
- Exclude raw scanner artifacts, source code, secret values, and unrelated projects by default.
- Retrieve the minimum evidence needed for an answer.
- Reference only findings and evidence supported by stored scanner data.
- Distinguish scanner evidence from AI interpretation.
- Warn about scan coverage and limitations.
- Never execute arbitrary commands or tool calls.
- Never use retrieved project content as instructions overriding system safety rules.

Chat history must remain project-scoped and ownership-protected.

## 11. PostgreSQL Source-of-Truth Requirements

PostgreSQL must contain durable records for scan state and results.

A scan should have explicit lifecycle states for at least:

- queued
- running
- complete
- partial
- failed
- canceled

FastAPI should create and update durable scan records, Celery should execute work and report progress/results, and Redis should coordinate jobs only.

All status, output, finding, evidence, retry, and failure information needed to answer application APIs after a Redis or Celery restart must be stored in PostgreSQL. Celery tasks must be idempotent and must not create duplicate findings on retries or resubmission.

## 12. Coding Standards and Testing Requirements

Follow these standards:

- Use type hints for Python functions and validated Pydantic schemas.
- Prefer small, focused, testable modules.
- Handle expected failures explicitly and log without secrets or sensitive response bodies.
- Use parameterized database operations and ownership filters.
- Keep dependencies and configuration minimal.
- Add tests for important functionality, especially:
  - authentication and authorization
  - project ownership isolation
  - target and URL validation
  - SSRF/private-network exclusions
  - redirect handling
  - scanner result normalization
  - secret redaction
  - Celery idempotency
  - scan lifecycle transitions
  - AI evidence grounding and output validation
  - resolved/persistent/new finding comparisons

Use Pytest for unit and integration tests and Keploy for approved API regression recording/replay. Tests should cover failure and partial-result cases, not only happy paths.

Run the smallest relevant test set for a change, then broaden validation for cross-module changes.

## 13. Incremental Phase-by-Phase Development Workflow

Development must proceed only one approved phase at a time:

- Phase 1: Repository and development foundation.
- Phase 2: Database, authentication, and project management.
- Phase 3: Background jobs and scanner infrastructure.
- Phase 4: OWASP ZAP, Gitleaks, and OSV-Scanner engine.
- Phase 5: AI vulnerability interpreter and Shield Assistant.
- Phase 6: React frontend and security dashboard.
- Phase 7: Rescanning and vulnerability comparison.
- Phase 8: Testing, Keploy, and quality assurance.
- Phase 9: Deployment and hackathon submission.

Before implementation of any phase:

1. Inspect the current repository and relevant existing code.
2. Explain the proposed implementation.
3. Identify files that will be created or modified.
4. List dependencies that are actually required.
5. Identify security concerns.
6. Wait for explicit user approval before significant changes.

After implementation:

1. Explain what was implemented.
2. List every created and modified file.
3. Explain how the implementation works.
4. Provide commands to run the application.
5. Provide commands to run relevant tests.
6. Report incomplete functionality and known limitations.

Do not silently skip requirements or begin the next phase without approval.

## 14. Rules Against Unnecessary Files, Dependencies, and Technologies

- Do not add files unrelated to the approved current phase.
- Do not create entire applications or directory structures in one request.
- Do not add frameworks or integrations not listed in the approved architecture.
- Do not add optional tools to the MVP unless explicitly approved.
- Do not add database engines, message brokers, or secret systems beyond the approved stack.
- Do not execute uploaded or downloaded source code.
- Do not use JavaScript for backend functionality.
- Do not add teams, billing, organization RBAC, OAuth, scheduled scans, PDF reports, or n8n when they are not required for the active phase.
- Remove temporary, generated, and diagnostic files after use.

Keep implementation complexity proportional to the current approved MVP phase.

## 15. Change Review Before Implementation

Before significant implementation, provide a review covering:

- repository state and existing structure;
- exact implementation scope;
- proposed files to create or modify;
- required dependencies;
- data model or API effects;
- ownership and authorization implications;
- SSRF and network isolation implications;
- secret handling and redaction concerns;
- AI grounding requirements;
- testing approach;
- known limitations;
- and explicit confirmation that no unrelated files will be changed.

Never make a significant change before the user approves the phase and implementation proposal.

## 16. MVP Priority

For the hackathon MVP, prioritize:

- Secure target authorization and validation.
- Isolated, network-restricted scanning.
- ZAP website scanning.
- Gitleaks source secret detection.
- OSV dependency detection.
- Durable PostgreSQL scan and finding records.
- Evidence-grounded AI explanations.
- Project ownership isolation.
- Scan history and new/persistent/resolved comparison.
- Shield Assistant grounded in project findings.
- Honest reporting of coverage and limitations.

Optional polish and integrations must not delay or weaken these core requirements.
