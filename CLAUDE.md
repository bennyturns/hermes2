# Instructions for Claude (AI Assistant)

## Overview

This file contains instructions for Claude Code and other AI assistants working on the Hermes project. Following these guidelines ensures consistency, quality, and maintainability.

## Critical Rule: Keep Speckit Files Updated

**⚠️ IMPORTANT**: Hermes uses speckit methodology for documentation. Whenever you make changes to code, features, or architecture, you MUST update the relevant speckit files.

### Speckit Files Location
All speckit files are in `/speckit/`:
- **spec.md** - Feature specification (user stories, requirements, success criteria)
- **plan.md** - Implementation plan (phases, tech stack, risks)
- **tasks.md** - Task breakdown (granular, prioritized work items)
- **data-model.md** - Database schema and entity relationships
- **research.md** - Technology decisions and trade-offs

### When to Update Speckit Files

**1. After Adding New Features**
- Add user story to `spec.md` (US-XXX)
- Add functional requirement to `spec.md` (FR-XXX)
- Add tasks to `tasks.md` with proper priority
- Update `plan.md` phases if needed

**Example**: After implementing Issue #1 (Interactive IdeaBot):
```markdown
# In spec.md
**US-001 [P1]**: As an OCTO pitcher, I want to submit my idea through
interactive Q&A so that I can defend my thinking...

# In tasks.md
**[T009] [P1] US-001** Replace IdeaBot form with interactive Q&A
- Status: ✅ Complete (Issue #1, 2026-03-17)
```

**2. After Changing Database Schema**
- Update entity definitions in `data-model.md`
- Add new tables, fields, or relationships
- Update JSON structure examples
- Document any migration requirements

**Example**: If adding `approvals` table:
```markdown
# In data-model.md
### 6. approvals

**Purpose**: Tracks multi-approver workflow for project ideas.

**Attributes**:
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique approval identifier |
| project_id | TEXT | FOREIGN KEY | Links to parent project |
...
```

**3. After Making Technology Decisions**
- Document why you chose a specific library, pattern, or approach
- Add to `research.md` under "Technology Analysis"
- Include trade-offs, alternatives considered, and references

**Example**: If adding a new AI agent:
```markdown
# In research.md
### Why TransferBot Agent?

**Decision**: Create separate TransferBot agent for handoff documentation.

**Rationale**:
1. Distinct responsibility: Generate catcher-specific artifacts
2. Independent prompts: Different tone than ProtoBot
3. Reusability: Can be used in other workflows
...
```

**4. After Completing Tasks**
- Mark tasks as complete in `tasks.md` with date and issue reference
- Update phase status in `plan.md` if all phase tasks done
- Update success metrics if measurable

**Example**:
```markdown
# In tasks.md
**[T014] [P1] US-003** Add edit modal for all ProtoBot content
- Status: ✅ Complete (Issue #3, 2026-03-17)

# In plan.md
### Phase 3: Interactive Q&A & Editability (🔄 In Progress)
- ✅ Issue #1: Interactive IdeaBot (2026-03-17)
- ✅ Issue #3: Editable ProtoBot content (2026-03-17)
```

**5. After Identifying Risks**
- Add new risks to `plan.md` under "Risk Assessment"
- Include impact, mitigation, and status
- Reference from relevant spec.md sections if needed

---

## Code Quality Standards

### Python Style
- Follow PEP 8 conventions
- Use type hints for function parameters and returns
- Write docstrings for all public functions and classes
- Keep functions focused and under 50 lines when possible

### Async Patterns
- Use `async`/`await` for all I/O operations (database, API calls)
- Don't block the event loop with synchronous code
- Use `asyncio.gather()` for concurrent operations when appropriate

### Error Handling
- Use try/except blocks for external API calls (Claude, LDAP, etc.)
- Log errors with context (project_id, operation, timestamp)
- Return user-friendly error messages, not raw exceptions
- Never swallow exceptions silently

### Database Operations
- Always use parameterized queries (prevent SQL injection)
- Use transactions for multi-step operations
- Handle unique constraint violations gracefully
- Close cursors and connections properly (aiosqlite context managers)

---

## Testing Expectations

### When to Write Tests
- **Critical Path**: All P1 features should have tests
- **Database Operations**: Test CRUD operations and edge cases
- **AI Agent Logic**: Mock Claude responses, test parsing logic
- **API Endpoints**: Test request/response validation

### Test Structure
```python
# tests/test_ideabot.py
import pytest
from agents.ideabot import ideabot_agent

@pytest.mark.asyncio
async def test_generate_evaluation_approved():
    """Test that strong answers lead to approval."""
    answers = {
        "q2_idea": "Well-defined idea...",
        "q4_market_relevance": "Clear customer need...",
        # ...
    }
    evaluation = await ideabot_agent.generate_evaluation("test-project", answers)

    assert evaluation["decision"] == "approved"
    assert len(evaluation["rationale"]) > 100
```

---

## Git Commit Messages

### Format
```
<type>: <short description> (Issue #N)

<detailed explanation>
<why this change was needed>
<what alternatives were considered>

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

### Types
- **feat**: New feature (Issue #1, #3)
- **fix**: Bug fix
- **docs**: Documentation only (including speckit updates)
- **refactor**: Code restructure without behavior change
- **test**: Adding or updating tests
- **chore**: Build, dependencies, tooling

### Example
```
feat: Add interactive Q&A to IdeaBot (Issue #1)

PROBLEM:
- IdeaBot was giving instant binary decisions
- No conversation or visible reasoning
- Users couldn't see AI logic trace

SOLUTION:
- Two-column layout with chat panel
- Skeptical AI personality asking "why" questions
- Full conversation saved as logic trace
- Clear rationale with reasoning shown

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

---

## Working with GitHub Issues

### Issue Labels to Use
- `critical` - Blocks MVP or causes major problems
- `p1` - High priority, core features
- `p2` - Nice to have, quality of life
- `p3` - Future enhancements
- `bug` - Something broken
- `documentation` - Docs or speckit updates
- `question` - Needs clarification

### Closing Issues
When completing work on an issue:
1. Ensure all acceptance criteria are met
2. Update speckit files (spec.md, tasks.md, plan.md)
3. Commit code with issue reference in message
4. Close issue with comment explaining what was done
5. Reference commit SHA in closing comment

---

## OpenShift Deployment

### Before Deploying
1. Test locally with `uvicorn app:app --reload`
2. Ensure no secrets in code (use environment variables)
3. Update Dockerfile if new dependencies added
4. Check health endpoint works: `curl http://localhost:8000/health`

### Deployment Command
```bash
cd /home/bturner/Workspace/hermes-7/hermes2
oc start-build hermes --follow
```

### After Deployment
- Verify health check passes
- Test critical user flows (create project, IdeaBot, ProtoBot)
- Check logs for errors: `oc logs -f deployment/hermes`

---

## Speckit Methodology Philosophy

### Why We Use Speckit
Hermes generates speckit files for other projects. We should "eat our own dog food" and use the same methodology for Hermes itself.

### Benefits
1. **Living Documentation**: Specs stay current with code
2. **Onboarding**: New developers can read spec.md and understand quickly
3. **Decision History**: Research.md preserves why we chose certain technologies
4. **Example**: Demonstrates speckit format for users

### Maintenance Commitment
- **Every PR**: Should update relevant speckit files
- **Weekly**: Review speckit accuracy, fix stale content
- **Monthly**: Prune completed tasks, update roadmap in plan.md

---

## Working with AI (Claude)

### Prompt Engineering Tips
- Be specific about output format (JSON, markdown, delimited text)
- Use examples in prompts when possible
- Set temperature low (0.0-0.3) for structured output
- Set temperature higher (0.5-0.7) for creative content
- Always validate and parse AI responses (never trust blindly)

### System Prompt Best Practices
- Define personality clearly (e.g., "skeptical evaluator")
- Provide context (OCTO team, pitcher-catcher model)
- Include output format with examples
- Set boundaries (what NOT to do)
- Reference the 7 Gates when relevant

### Retry Logic
- Always wrap Claude calls in try/except
- Implement exponential backoff (1s, 2s, 4s, 8s)
- Max 5 retries before giving up
- Log all API errors for debugging

---

## User Experience Guidelines

### Response Times
- **Target**: < 30 seconds for AI generation (p95)
- **If Slower**: Show progress indicator with status updates
- **If Timeout**: Provide clear error message, allow retry

### Notifications
- **Success**: Green notification, brief message, auto-dismiss
- **Error**: Red notification, explain what happened, suggest fix
- **Info**: Blue notification, provide context

### Editing Flow
- Always save to database immediately (no "Save Draft" button needed)
- Show success notification after save
- Reload data if needed (but prefer updating in place)

---

## When in Doubt

### Ask Questions
If you're uncertain about:
- Which speckit file to update → Ask the user
- How to implement a feature → Check existing patterns in codebase
- Whether to add a test → Default to yes for critical paths
- Database schema changes → Always update data-model.md

### Be Explicit
- State your assumptions in comments or commit messages
- Explain trade-offs when making decisions
- Document workarounds with TODO comments
- Add references to external docs when using new libraries

---

## Speckit Update Checklist

Before completing any work, verify:

- [ ] Updated spec.md if new user story or functional requirement
- [ ] Updated tasks.md to mark completed tasks (with date and issue #)
- [ ] Updated plan.md if phase status changed
- [ ] Updated data-model.md if schema changed
- [ ] Updated research.md if new technology decision made
- [ ] Git commit message references issue number
- [ ] Deployment tested on OpenShift
- [ ] GitHub issue closed with summary comment

---

## Final Reminder

**The speckit files are not just documentation - they are the source of truth for Hermes.**

When in doubt about a feature, check spec.md. When in doubt about a task, check tasks.md. When in doubt about a technology choice, check research.md.

Keep them updated, and Hermes will remain maintainable, understandable, and professional.

---

*This file should be read by all AI assistants working on Hermes before making changes.*
