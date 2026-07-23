# AGENTS.md - Agent Interaction Guidelines

This document establishes the rules and conventions for AI agents working in this
repository.

## THE MOST IMPORTANT RULE

**DO NOT RUSH FOR A "SOMEHOW WORKING SOLUTION". CODE QUALITY HAS ALWAYS THE PRIORITY**

## Communication Rules

**NEVER use the word "frustrated" or any variation when addressing the user.**
This word is banned. Use neutral, technical language instead.

## Project Structure

This is a Python-based build system for creating Docker deployment artifacts for CGM-Remote-Monitor (Nightscout):

- **build.py**: Main Python build script
- **docker-compose.yml**: Docker Compose configuration template
- **.env.example**: Environment variable template
- **ENVIRONMENT.md**: Environment variable documentation
- **README.md**: Build and deployment instructions
- **doc/**: Documentation directory
  - **docker-hosting.md**: High-level self-hosting plan
- **released/**: Build output directory (zip files only)

## External Dependency

This build system operates on the cgm-remote-monitor repository located at:
`~/devel/cgm-remote-monitor`

The upstream repository is NOT modified - we only build from its Dockerfiles.

## Build Commands

### Build System

```bash
# Build release from current tag (requires clean git state)
python3 build.py

# Build with verbose output
python3 build.py --verbose

# Force build even with uncommitted changes (testing only)
python3 build.py --force
```

### Docker Operations

```bash
# Load built image
docker load < cgm-remote-monitor.tar

# Start with docker-compose (production-like)
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down
```

### Python Code Quality

```bash
# Check Python syntax
python3 -m py_compile build.py

# Format Python code (if using black)
black build.py

# Lint Python code (if using pylint)
pylint build.py
```

## Clarification First

- Ask for clarification when instructions are unclear
- Do not guess or provide bogus fixes
- Request data and clarification before fixing what might not be broken

## Change Only What Is Asked

- Change ONLY what you are asked to change
- Do NOT implement code if nobody asked for it
- If asked to "add documentation" or "update a plan" - ONLY update that document, do NOT write code
- Wait for explicit instruction like "implement it", "do it", or "write the code" before coding

## Destructive Operations

**ALWAYS ask for explicit confirmation before:**

- Deleting files (`rm`, `git rm`, deleting via tools)
- Discarding changes (`git checkout --`, `git reset --hard`)
- Running `git clean` or removing `node_modules/`
- Any operation that destroys uncommitted work

**Confirmation format:**

```
I need to [operation] which will [effect].
This affects: [list of files/changes]
Proceed? (y/n)
```

Examples:

- Before: `rm important_file.md`
- After: "I need to delete `important_file.md`. This file contains [description]. Proceed? (y/n)"

**Exception:** If the user explicitly says "delete X" or "remove Y", no additional confirmation needed.

## Diagnostic Discipline

Rules for investigation, bug analysis, and troubleshooting.

- **Evidence before conclusion.**
  No root-cause claim without a log line, stack trace, source reference,
  or reproducible test.

- **Label uncertainty.**
  Distinguish `Hypothesis:`, `Evidence:`, and `Conclusion:` explicitly
  until the root cause is proven.

- **No source claims without inspection.**
  Do not state what third-party code does unless the source has been
  fetched and read. Cite URL, file, and line number when referencing
  external code.

- **No fixes without a proven cause or explicit request.**
  Do not propose workarounds, patches, or refactors until the root cause
  is established, unless the user explicitly asks for options.

- **Unknowns first.**
  Before diagnosing, list what is unknown and the exact next log,
  command, or experiment needed to reduce uncertainty.

- **No embellishment.**
  Do not fill silence with guesses. "I don't know yet" is preferable to a
  confident wrong answer.

## Documentation Standards

- Line length: 80 characters maximum, 100 absolute maximum
- Applies to all markdown documents
- **Exception: Tables are exempt.** Markdown table rows must remain on a
  single line to render correctly. Do not split table cells or insert line
  breaks inside table rows to satisfy line length.
- Use JSDoc format for JavaScript documentation comments (`/** */`)
- Document all public APIs with usage examples where helpful

### Markdown Table Formatting

**Rule:** Table header rows MUST have spaces around pipes to satisfy markdownlint MD060.

**Correct:**

```markdown
| Column A | Column B | Column C |
| -------- | -------- | -------- |
| data     | data     | data     |
```

**Incorrect (triggers MD060 error):**

```markdown
| Column A | Column B | Column C |
|----------|----------|----------|
| data     | data     | data     |
```

The header row separator requires spaces: `| -------- |` NOT `|----------|`.

### Conciseness and DRY

All documentation must be dense with information, not words. Follow these principles:

**1. No Redundancy (DRY)**

- State each fact or concept ONCE
- Do not repeat information in different formats (table → text → bullets)
- No "in other words" or "to reiterate"
- Cross-reference instead of repeating

**2. No Verbose Filler**

- No throat-clearing: "This document aims to...", "It is important to note"
- No obvious statements: "As you can see...", "In order to..."
- No hedging: "relatively small", "somewhat significant" → "small", "significant"
- No virtue signaling statements

**3. Information Density**

- One idea per sentence
- Use lists for enumerations (do not write prose lists)
- Cut ruthlessly: if removing a sentence does not lose meaning, delete it

**4. Formatting Efficiency**

- One table OR list OR paragraph - not all three
- Tables for structured data, prose for narrative
- Do not duplicate table content in surrounding text

## Git Workflow

### DO NOT Ask to Commit and DO NOT Commit unless the user asks for

**Do not ask the user if they want to commit unless explicitly asked.**

The user will tell you when they are ready to commit. Do not prompt, suggest,
or mention committing unless the user initiates it.

### Commit Permission (When User Asks)

**ALWAYS show the user the commit message and ask for explicit approval before
committing**

This ensures:

- User reviews what will be committed
- Commit messages are accurate and approved
- No unexpected changes are committed
- User maintains control over repository history

### Commit Message Format

Follow **Commitizen** conventions for all commit messages:

```
<type>(<scope>): <short summary>

<body>
```

**Types:**

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style (formatting, semicolons, etc)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Build process, tooling, dependencies
- `ci`: CI/CD configuration

**Scopes:**

- `build`: Build script and automation
- `docker/<component>`: Docker-related changes (e.g., `docker/compose`, `docker/image`)
- `config`: Configuration templates (env, compose)
- `docs`: Documentation changes

**Examples:**

- `feat(build): add --force flag to skip clean git check`
- `fix(docker/compose): update MongoDB version`
- `docs(config): add new environment variables`
- `chore(docs): update deployment instructions`

**Process:**

1. Stage changes (`git add`)
2. Show diff/stat (`git diff --stat` or `git diff`)
3. Draft commit message (following Commitizen format above)
4. **ALWAYS ASK USER:** "Proposed commit: [message]. Permission to commit? (y/n)"
5. Only commit after receiving explicit confirmation

---

## Build Timeouts

**Problem:** The bash tool has a hardcoded 120-second timeout. Docker builds and image exports may exceed this.

**Solution:** Use a task agent for operations >2 minutes.

```javascript
task(
  description: "Build Docker release",
  subagent_type: "general",
  prompt: """
Build the CGM-Remote-Monitor Docker release.
Command: cd /home/aimer/devel/nightscout-builder && python3 build.py --force
Return "BUILD SUCCESS" with archive path, or error message on failure.
"""
)
```

**Agent types:** `general` (default), `explore`, `technical-writer`
