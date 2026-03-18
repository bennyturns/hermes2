# Research: Hermes Technology Decisions

## Technology Analysis

### Why FastAPI?

**Decision**: Use FastAPI as the web framework instead of Flask or Django.

**Rationale**:
1. **Async/Await Native**: FastAPI built on Starlette with first-class async support, critical for AI API calls that can take 10-30 seconds
2. **Performance**: ASGI server (Uvicorn) significantly faster than WSGI, handles concurrent requests efficiently
3. **Type Safety**: Pydantic integration provides automatic request/response validation and documentation
4. **Developer Experience**: Auto-generated OpenAPI docs, excellent error messages, minimal boilerplate

**Trade-offs**:
- **Pro**: Modern Python features (3.7+ type hints), excellent for APIs
- **Pro**: Strong community momentum, well-maintained
- **Con**: Less mature than Flask/Django, fewer third-party integrations
- **Con**: Learning curve for developers unfamiliar with async patterns

**Evidence**: FastAPI is [one of the fastest Python frameworks](https://www.techempower.com/benchmarks/#section=data-r21&hw=ph&test=fortune) and has excellent async support for AI workloads.

---

### Why SQLite (MVP) → PostgreSQL (Production)?

**Decision**: Start with SQLite for MVP, migrate to PostgreSQL for production.

**Rationale**:
1. **SQLite for MVP**:
   - Zero configuration, embedded database
   - Perfect for ephemeral OpenShift environment
   - Fast development iteration
   - Sufficient for single-user/low-concurrency (<10 concurrent projects)

2. **PostgreSQL for Production**:
   - Better concurrency (row-level locking vs. database-level)
   - Superior JSON query capabilities (JSONB type)
   - Production-ready with replication, backups
   - Red Hat infrastructure standard

**Trade-offs**:
- **Pro (SQLite)**: Simple deployment, no external dependencies, fast for small datasets
- **Con (SQLite)**: Limited concurrency, no network access, manual backups
- **Pro (PostgreSQL)**: Scalable, robust, excellent JSON support
- **Con (PostgreSQL)**: Requires separate deployment, more complex operations

**Migration Path**: Use Alembic for schema versioning, SQLAlchemy ORM for database abstraction (future enhancement).

---

### Why Claude AI (Anthropic) via Vertex?

**Decision**: Use Anthropic's Claude via Google Vertex AI instead of OpenAI GPT or local models.

**Rationale**:
1. **Quality**: Claude Sonnet 4.5 excellent for structured output, reasoning, and long-context tasks
2. **Vertex Integration**: Red Hat has existing Vertex AI contracts and infrastructure
3. **Context Window**: 200K tokens sufficient for full conversation history + system prompts
4. **Structured Output**: Strong at following format instructions (JSON, delimited text)
5. **Safety**: Anthropic's constitutional AI reduces harmful outputs

**Trade-offs**:
- **Pro**: Best-in-class reasoning, excellent at "skeptical evaluation" personality
- **Pro**: Cost-effective for OCTO use case (~100-200 requests/week)
- **Con**: External dependency, network latency (500-2000ms per request)
- **Con**: Vendor lock-in (migrating prompts to other models requires retuning)

**Alternatives Considered**:
- **OpenAI GPT-4**: Similar quality, but no existing Red Hat contract
- **Local Models (Llama 3, Mistral)**: Free inference but lower quality, requires GPU infrastructure
- **Red Hat InstructLab**: Future option when model quality matches Claude

**References**:
- [Anthropic Claude Documentation](https://docs.anthropic.com/claude/reference/getting-started-with-the-api)
- [Vertex AI Claude Integration](https://cloud.google.com/vertex-ai/generative-ai/docs/partner-models/use-claude)

---

### Why Jinja2 (Server-Side Rendering) vs. React/Vue?

**Decision**: Use Jinja2 templates with vanilla JavaScript instead of a frontend framework.

**Rationale**:
1. **Simplicity**: OCTO use case is internal tool, not public SaaS product
2. **Fast Development**: No build step, no npm dependencies, no bundling
3. **SEO/Accessibility**: Server-rendered HTML works without JavaScript
4. **Easier Deployment**: Single FastAPI container, no separate frontend build

**Trade-offs**:
- **Pro**: Simple, fast iteration, no JavaScript framework complexity
- **Pro**: Less code to maintain, fewer dependencies
- **Con**: More page reloads (mitigated with AJAX for key interactions)
- **Con**: Limited interactivity compared to React/Vue (acceptable for MVP)

**Future Enhancement**: Consider htmx for progressive enhancement if interactivity needs grow.

---

### Why OpenShift Ephemeral Environment?

**Decision**: Deploy to OpenShift ephemeral environment for MVP testing.

**Rationale**:
1. **Red Hat Standard**: OpenShift is the standard deployment platform
2. **Fast Provisioning**: Ephemeral environments spin up quickly for testing
3. **Cost-Effective**: No long-running resources, only active during development
4. **Production-Like**: Same platform as final production deployment

**Trade-offs**:
- **Pro**: Easy to provision, integrated with Red Hat infrastructure
- **Pro**: Container-based deployment matches production
- **Con**: Data loss on pod restarts (ephemeral storage)
- **Con**: Not suitable for long-term storage (need persistent volumes for production)

**References**:
- [OpenShift Documentation](https://docs.openshift.com/)
- [Ephemeral Storage Guide](https://docs.openshift.com/container-platform/4.13/storage/understanding-ephemeral-storage.html)

---

## Architectural Decisions

### Agent-Based Design Pattern

**Decision**: Separate AI agents for each workflow (IdeaBot, ProtoBot, SpecKit, Transfer).

**Rationale**:
1. **Separation of Concerns**: Each agent has distinct system prompt and responsibilities
2. **Independent Evolution**: Can update IdeaBot prompt without affecting ProtoBot
3. **Reusability**: Agents can be composed (e.g., SpecKit agent used in QuickProto and ProtoBot)
4. **Testability**: Easy to test each agent in isolation

**Implementation**:
```python
# agents/ideabot.py
class IdeaBotAgent:
    async def chat(self, project_id, message):
        # Skeptical evaluation with "why" questions
        pass

    async def generate_evaluation(self, project_id, answers):
        # Final decision with rationale
        pass

# agents/blueprint_agent.py
class BlueprintAgent:
    async def generate_research(self, project_id, context):
        # Market + technical research
        pass

    async def generate_blueprint(self, project_id, research):
        # Architecture + implementation plan
        pass
```

**References**:
- [Agent Pattern in AI Applications](https://www.anthropic.com/research/building-effective-agents)

---

### Conversation State Management

**Decision**: Store all chat history in database, not in-memory sessions.

**Rationale**:
1. **Persistence**: Conversations survive pod restarts
2. **Auditability**: Full "logic trace" for decision explanation
3. **Debugging**: Can replay conversations to understand AI behavior
4. **Multi-Device**: User can switch devices and continue conversation

**Implementation**:
- `conversation_messages` table with (project_id, context, role, content, created_at)
- Load full history on each AI request
- Context-aware: IdeaBot vs. ProtoBot conversations kept separate

**Trade-offs**:
- **Pro**: Durable, auditable, supports "logic tracing" requirement
- **Con**: Database grows with chat history (mitigated by pruning old conversations)

---

### JSON Storage in SQLite Text Fields

**Decision**: Store structured data (answers, evaluation, research, blueprint) as JSON in TEXT fields.

**Rationale**:
1. **Flexibility**: Schema can evolve without database migrations
2. **Simplicity**: No complex JOIN queries for related data
3. **AI Integration**: Claude outputs JSON naturally, easy to store directly
4. **SQLite Limitation**: No native JSON type (PostgreSQL has JSONB)

**Trade-offs**:
- **Pro**: Fast development, flexible schema, easy serialization
- **Con**: No database-level JSON validation, harder to query specific fields
- **Con**: Need application-level parsing and validation

**Migration to PostgreSQL**:
- Convert TEXT fields to JSONB for better query performance
- Add GIN indices on frequently queried JSON fields
- Use PostgreSQL JSON functions for filtering

---

## External Dependencies

### Critical Dependencies
1. **anthropic[vertex]==0.40.0**: Claude AI SDK with Vertex integration
2. **fastapi==0.109.0**: Web framework
3. **uvicorn[standard]==0.27.0**: ASGI server with WebSocket support
4. **aiosqlite==0.19.0**: Async SQLite driver
5. **jinja2==3.1.3**: Template engine
6. **pydantic==2.6.0**: Data validation

### Dependency Risks
- **Anthropic SDK**: Breaking changes in major versions (mitigated by version pinning)
- **FastAPI**: Rapid development, occasional breaking changes (mitigated by testing)
- **SQLite**: No network protocol, single-writer limitation (plan to migrate to PostgreSQL)

### Dependency Management
- Pin exact versions in requirements.txt
- Test updates in staging before production
- Monitor security advisories (GitHub Dependabot)

---

## Performance Considerations

### AI Response Times
- **Typical**: 5-10 seconds for conversational responses
- **Peak**: 20-30 seconds for complex artifact generation
- **Optimization**: Stream responses for better UX (future enhancement)

### Database Query Performance
- **Current**: < 100ms for most queries (small dataset)
- **Projected**: May need indices when dataset grows > 1000 projects
- **Monitoring**: Add query timing logs to identify slow queries

### Concurrent Users
- **MVP Target**: 5-10 concurrent users
- **SQLite Bottleneck**: Single writer, concurrent reads OK
- **Solution**: Migrate to PostgreSQL when concurrency needs exceed SQLite capability

---

## Security Considerations

### API Key Management
- **Current**: Stored as OpenShift secrets, injected as environment variables
- **Access**: Only application pod can read secrets
- **Rotation**: Manual process (future: automate key rotation)

### Input Validation
- **User Input**: Validated by Pydantic models before database writes
- **AI Output**: Parsed and validated before storage (reject malformed JSON)
- **SQL Injection**: Protected by parameterized queries (aiosqlite)

### Prompt Injection
- **Risk**: User could manipulate AI via crafted inputs
- **Mitigation**: System prompts hardened, output validation, content filtering
- **Future**: Add input sanitization, output redaction for sensitive data

---

## References

### Framework Documentation
- [FastAPI Official Docs](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Jinja2 Template Designer](https://jinja.palletsprojects.com/)

### AI Integration
- [Anthropic Claude API Reference](https://docs.anthropic.com/claude/reference/messages_post)
- [Vertex AI Partner Models](https://cloud.google.com/vertex-ai/generative-ai/docs/partner-models/use-claude)
- [Building Effective AI Agents](https://www.anthropic.com/research/building-effective-agents)

### Deployment
- [OpenShift Developer Guide](https://docs.openshift.com/container-platform/4.13/welcome/index.html)
- [Container Best Practices](https://developers.redhat.com/articles/2021/11/11/best-practices-building-images-pass-red-hat-container-certification)

### Database
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [aiosqlite GitHub](https://github.com/omnilib/aiosqlite)
- [PostgreSQL JSONB](https://www.postgresql.org/docs/current/datatype-json.html)

### Async Python
- [Python asyncio Documentation](https://docs.python.org/3/library/asyncio.html)
- [Real Python Async IO Tutorial](https://realpython.com/async-io-python/)
