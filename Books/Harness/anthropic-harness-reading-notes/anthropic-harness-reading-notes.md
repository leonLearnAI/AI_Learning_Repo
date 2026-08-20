# Reading Notes: Anthropic Harness Engineering Series
*Six articles tracing the conceptual and engineering arc from basic agent patterns to production-grade multi-agent harness design.*

---

## Article 1 — Building Effective Agents
**Published:** Dec 19, 2024
**URL:** https://www.anthropic.com/research/building-effective-agents

### Core Distinction: Workflow vs. Agent

All LLM-based systems are **agentic systems**, but internally split into two architectural categories:

- **Workflow** — execution paths are controlled by predefined code. The LLM is a component, not the decision-maker.
- **Agent** — the LLM dynamically directs its own processes and tool usage. Control over how tasks are accomplished belongs to the model.

This is not a taxonomy of sophistication but a question of **who holds control**: code or model.

**Default posture:** start with the simplest solution. Many tasks are fully solved by a well-engineered single LLM call with retrieval and few-shot examples. Agentic systems trade latency and cost for task performance — only pay that cost when the tradeoff is demonstrably worth it.

---

### Building Block: The Augmented LLM

The foundational unit of all agentic systems is an LLM augmented with three capabilities:

- **Memory** — storing and recalling information
- **Tools** — calling external actions and APIs
- **Retrieval** — actively generating search queries to find relevant context

The model *actively* uses these — generating its own queries, selecting tools, deciding what to retain — rather than passively receiving inputs.

---

### Five Workflow Patterns (complexity order)

**1. Prompt Chaining**

Decomposes a task into a fixed sequence of LLM calls, where each call processes the output of the previous one. Programmatic gates can be inserted at any step to validate intermediate results.

```
Input → LLM₁ → [Gate] → LLM₂ → [Gate] → LLM₃ → Output
```

*Use when:* task decomposes cleanly into fixed sequential subtasks. Trades latency for higher accuracy per step.
*Example:* generate marketing copy → compliance gate → translate to target language.

**2. Routing**

Classifies the input first, then routes to a specialized downstream process. Enables separation of concerns — each route can have its own optimized prompt without competing with others.

```
Input → Classifier → Route A / Route B / Route C
```

*Use when:* inputs fall into distinct categories that are better handled separately, and classification can be done reliably.
*Example:* route easy questions to Haiku, complex ones to Sonnet. Route refund requests, technical support, and general inquiries to separate specialist flows.

**3. Parallelization — two variants**

*Sectioning:* break a task into independent subtasks and run them simultaneously. Aggregator synthesizes results.

```
Input → [LLM-A | LLM-B | LLM-C] → Aggregator → Output
```

*Voting:* send the same task to multiple independent LLM instances. Majority vote or threshold determines final output.

```
Input → [Instance-1 | Instance-2 | Instance-3] → Vote → Output
```

*Use sectioning when:* subtasks are independent and benefit from dedicated attention.
*Use voting when:* single-shot reliability is insufficient and independent verification adds confidence.
*Example sectioning:* one instance handles the user query, a second simultaneously runs content safety screening — better than asking one model to do both.
*Example voting:* multiple prompts independently flag security vulnerabilities in code; only flag if consensus reached.

**4. Orchestrator-Workers**

A central LLM (Orchestrator) *dynamically* decomposes the task, delegates to Worker LLMs, and synthesizes results. Unlike Sectioning, subtasks are not predefined — the Orchestrator determines them based on the specific input at runtime.

```
Orchestrator (dynamic decomposition)
    ↓           ↓           ↓
 Worker-A    Worker-B    Worker-C
    ↓           ↓           ↓
         Synthesized Output
```

*Use when:* the number and nature of subtasks cannot be hardcoded in advance.
*Example:* complex codebase changes — which files to modify and how depends on the specific task, not a fixed recipe.

**5. Evaluator-Optimizer**

One LLM generates output; a second LLM evaluates and provides feedback. Loop repeats until quality threshold is met.

```
Input → Generator → output → Evaluator → feedback
                ↑________________________________|
                        (loop until pass)
```

*Two signals of good fit:*
1. LLM output demonstrably improves when a human articulates feedback — meaning iteration has real value.
2. The LLM can itself provide that kind of feedback — meaning automation is viable.

If only signal 1 is present: the evaluator can't give meaningful feedback, loop produces noise.
If only signal 2 is present: feedback is generated but doesn't actually improve output, loop is wasted computation.

*Example:* literary translation — nuances require multiple refinement passes; an evaluator LLM can articulate what's lost and why.

---

### Autonomous Agents

Agents are LLMs using tools based on environmental feedback, operating in a loop:

```
Human/Environment input
    ↓
[Agent Loop]
  LLM decides next tool → execute tool → observe result → repeat
    ↓ (task complete / stopping condition reached)
Output
```

*Use when:* the task is open-ended, the number of required steps cannot be predicted, and a fixed execution path cannot be hardcoded. Trust in the model's decision-making is required.

*Cost:* higher latency, higher token spend, compounding error risk. Test extensively in sandboxed environments. Set stopping conditions (e.g., max iterations) as guardrails.

---

### ACI: Agent-Computer Interface

Tools deserve the same engineering attention as prompts. The ACI is to agents what HCI is to humans.

Design principles:
- **Give the model thinking room** before it commits to an action — enough tokens to reason before writing itself into a corner.
- **Format should match training distribution** — keep tool formats close to what naturally appears in text. JSON with escaped code is harder than Markdown with code blocks.
- **Eliminate formatting overhead** — never require the model to maintain accurate line counts or complex escape sequences.
- **Poka-yoke the parameters** — make the wrong input structurally harder to produce than the right one.
- **Write tools like docstrings for a junior developer** — include example usage, edge cases, input format requirements, and clear boundaries from adjacent tools.

*Concrete case:* in SWE-bench work, changing a file tool from relative to absolute filepath requirement eliminated a class of errors entirely. More time was spent optimizing tools than the main prompt.

---

### Three Core Principles

1. **Simplicity** — keep agent design simple. Complexity is a cost, not a virtue.
2. **Transparency** — explicitly show the agent's planning steps.
3. **ACI quality** — invest in tool documentation and testing as seriously as prompt engineering.

Add complexity only when it demonstrably improves outcomes.

---

## Article 2 — How We Built Our Multi-Agent Research System
**Published:** Jun 13, 2025
**URL:** https://www.anthropic.com/engineering/built-multi-agent-research-system

### Why Multi-Agent for Research

Research tasks are fundamentally open-ended — the path is path-dependent, and intermediate findings reshape subsequent directions. A linear single-pass pipeline cannot handle this. Key properties:

- Cannot predict required steps in advance
- Must operate autonomously across many turns
- Needs to pivot as new information emerges

The core value of subagents in this context is **compression**: each subagent explores extensively within its own isolated context window, then returns only a distilled summary (typically 1,000–2,000 tokens) to the lead agent. This keeps the lead agent's context clean and focused while enabling broad parallel exploration.

---

### Architecture

```
User Query
    ↓
LeadResearcher (Opus 4)
  ├─ Writes research plan to Memory (persisted outside context)
  ├─ Spawns Subagent-1 → direction A
  ├─ Spawns Subagent-2 → direction B
  └─ Spawns Subagent-N → direction N
         ↓ each returns distilled summary
LeadResearcher synthesizes
  ├─ Sufficient? → proceed
  └─ Insufficient? → spawn additional subagents
         ↓
CitationAgent (processes citations independently)
         ↓
Final output to user
```

*Why Memory for the research plan:* context windows exceeding 200,000 tokens get truncated. The plan must survive truncation, so it is written to external memory before exploration begins.

*Why a separate CitationAgent:* citation accuracy requires dedicated attention — a general-purpose agent handling citations alongside synthesis produces lower-quality attribution.

---

### Key Performance Data

- Multi-agent system (Opus 4 lead + Sonnet 4 subagents) outperformed single-agent Opus 4 by **90.2%** on internal research eval.
- Token usage alone explains **80%** of performance variance on BrowseComp benchmark.
- Multi-agent systems consume approximately **15× more tokens** than standard chat interactions.
- Upgrading subagents from Sonnet 3.7 to Sonnet 4 produced a larger performance gain than doubling the token budget — model capability acts as a multiplier on token efficiency.

---

### Eight Prompt Engineering Principles for Multi-Agent Systems

**1. Think like your agents**
Build simulations in Console using exact production prompts and tools. Watch agents work step by step. This immediately surfaces failure modes: continuing after sufficient results, overly verbose queries, wrong tool selection. Accurate mental models of agent behavior make the most impactful fixes obvious.

**2. Teach the orchestrator to delegate precisely**
Early versions allowed short vague instructions. Result: three subagents investigated the same semiconductor shortage from overlapping angles with no effective division of labor. Each subagent description must include: objective, output format, tool and source guidance, and explicit task boundaries relative to other subagents.

**3. Scale effort to query complexity**
Embed explicit resource allocation rules in the prompt:
- Simple fact-finding: 1 subagent, 3–10 tool calls
- Direct comparison: 2–4 subagents, 10–15 calls each
- Complex research: 10+ subagents with clearly divided responsibilities

Without this, agents over-invest in simple queries — the most common early failure mode.

**4. Tool design and selection are critical**
Give agents explicit heuristics: examine all available tools first, match tool to user intent, prefer specialized tools over generic ones, use web search for broad external exploration. Bad tool descriptions send agents down entirely wrong paths. Each tool needs a distinct purpose and a clear description.

**5. Let agents improve themselves**
Claude 4 models can act as prompt engineers. Given a flawed MCP tool, an agent can attempt to use it, diagnose failure modes, and rewrite the tool description. After testing dozens of times, the new description reduced task completion time for subsequent agents by **40%**.

**6. Start wide, then narrow**
Search strategy should mirror expert human research: short broad queries first to map the information landscape, then progressively narrow. Agents default to overly specific long queries that return few results — counter this tendency explicitly in the prompt.

**7. Guide the thinking process**
Lead agent uses extended thinking to plan: which tools fit the task, how many subagents to spawn, role definitions. Subagents use interleaved thinking after each tool result to evaluate quality, identify gaps, and refine the next query. Extended thinking improved instruction-following, reasoning quality, and efficiency.

**8. Parallel tool calling**
Early agents used sequential search — painfully slow. Two layers of parallelization: (1) lead agent spawns 3–5 subagents simultaneously rather than serially; (2) each subagent calls 3+ tools in parallel. These changes reduced research time by up to **90%** for complex queries.

---

### Evaluation Strategy

**Why standard evaluation fails:** multi-agent systems are non-deterministic — two valid paths to the same answer may look completely different. You cannot check whether agents followed a prescribed path. Evaluate outcomes, not steps.

**Start immediately with small samples:** early-stage changes have large effects (30% → 80% success rates). 20 representative test cases are sufficient to see signal. Don't wait for a large eval set to begin testing.

**LLM-as-judge at scale:** judge on: factual accuracy, citation accuracy, completeness, source quality, tool efficiency. Single LLM with unified prompt outputting 0.0–1.0 scores plus pass/fail was more consistent and better aligned with human judgment than multiple judges evaluating separate dimensions.

**Human evaluation catches what automation misses:** human testers discovered systematic bias toward SEO-optimized content farms over authoritative sources (academic PDFs, official sites). No automated eval caught this. Source quality heuristics were added to prompts to correct it.

---

### Production Engineering Challenges

**Errors compound:** a single step failure can push the agent onto a completely different trajectory. Cannot restart from scratch — too costly. Solution: build resume-from-checkpoint systems; also let the model know when a tool is failing and allow it to adapt. Combine AI adaptability with deterministic safeguards (retry logic, regular checkpoints).

**Non-deterministic debugging:** same prompt, different run, different path. Added full production tracing monitoring decision patterns and interaction structures — without logging individual conversation contents (privacy). High-level observability enables root cause diagnosis without privacy violation.

**Rainbow Deployment for stateful agents:** standard blue-green deployment would instantly cut off in-progress agents. Rainbow Deployment keeps both old and new versions running simultaneously, gradually shifting new traffic to the new version while old agents run to natural completion.

**Synchronous execution bottleneck (current limitation):** lead agent waits for each batch of subagents to complete before proceeding. Blocked by slowest subagent; cannot steer mid-research. Async execution would enable additional parallelism but introduces state consistency and error propagation complexity.

---

### Appendix Techniques

**End-state evaluation:** for agents that mutate state across turns, evaluate the final state rather than individual steps. Break complex workflows into discrete checkpoints.

**Long-horizon conversation management:** when context approaches limits, agents summarize completed phases, store essential info in external memory, spawn fresh subagents with clean contexts via careful handoffs. Research plan retrieved from memory rather than lost on truncation.

**Subagent output to filesystem:** subagents store results in external systems and pass lightweight references back to lead agent. Prevents information loss through multi-stage processing and reduces token overhead from copying large outputs through conversation history.

---

## Article 3 — Effective Context Engineering for AI Agents
**Published:** Sep 29, 2025
**URL:** https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents

### Definition

**Context** = the complete set of tokens included when sampling from an LLM: system prompt, tools, MCP definitions, external data, message history — everything in the window.

**Context engineering** = the set of strategies for curating and maintaining the optimal set of tokens during LLM inference, at every inference step.

Relationship to prompt engineering:

| | Prompt Engineering | Context Engineering |
|---|---|---|
| Focus | Writing instructions | Managing the entire token state |
| Timing | One-time task | Every inference step |
| Scope | System prompt | All context components |

As agents run in loops generating more data each turn, context engineering answers: from the constantly expanding universe of potentially relevant information, what enters the window right now?

---

### Why Context Must Be Treated as a Finite Resource

**Mechanism 1 — Context rot:** as token count increases, the model's ability to accurately recall information from that context decreases. This is a performance gradient, not a hard cliff — attention degrades progressively.

**Mechanism 2 — Transformer n² problem:** the Transformer architecture requires every token to attend to every other token, producing n² pairwise relationships for n tokens. As context grows, this relationship network expands quadratically, thinning out attention per token pair.

**Mechanism 3 — Training distribution mismatch:** short sequences are far more common than long sequences in training data. Models have less specialized capacity for long-context dependencies. Even with position encoding interpolation extending window size, precision degrades at longer contexts.

**Engineering conclusion:** larger context windows do not solve the problem. Context must be managed as an attention budget — spent deliberately, not accumulated passively.

---

### Design Principles for Each Context Component

**System Prompt — finding the right altitude**

Two failure extremes:
- *Too specific:* hardcoded if-else logic for every case. Brittle, high maintenance, fails on any edge case not explicitly covered.
- *Too vague:* high-level guidance that falsely assumes shared context. LLM lacks concrete behavioral signals, output becomes unpredictable.

The right altitude: specific enough to guide behavior effectively, flexible enough for the model to handle edge cases through heuristics rather than lookup.

Practical guidance: organize with XML tags or Markdown headers (`<instructions>`, `## Tool guidance`, `<background_information>`). Start with the minimum prompt that describes expected behavior on the best available model. Add instructions and examples based on observed failure modes — never preemptively.

**Tools — minimal viable set**

Most common failure mode: bloated toolsets with functional overlap create ambiguous decision points. If a human engineer cannot definitively say which tool to use in a given scenario, the agent cannot be expected to do better. Each tool should have a clearly distinct purpose with no overlap.

Tools also consume context budget through their definitions — every tool added is context spent.

**Few-shot Examples — quality over quantity**

Do not enumerate every edge case. Curate a diverse, canonical set that effectively conveys expected behavioral patterns. For an LLM, a well-chosen example is worth a thousand words of rule description.

---

### Just-in-Time Context: Runtime Loading

**Traditional RAG (static):** pre-inference retrieval — fetch most similar chunks, load into context before reasoning begins. One-time, upfront decision about what goes in.

**Just-in-time (dynamic):** context holds lightweight identifiers (file paths, stored queries, web links). Agent uses tools to load specific content on demand, only when needed for the current step.

```
Traditional RAG:
Pre-inference → retrieve chunks → load all → reason

Just-in-time:
Maintain identifiers → reason → need data → fetch → continue
```

**Claude Code as canonical example:** uses `grep`, `tail`, `head` to analyze large files without loading them fully. `CLAUDE.md` files are pre-loaded at startup (stable project-level context). Specific source files are retrieved just-in-time via glob/grep (dynamic code content). This is a **hybrid strategy** — stable content pre-loaded, dynamic content fetched on demand.

**Additional benefit — progressive disclosure:** metadata itself is signal. File size implies complexity; naming conventions imply purpose; timestamps are a proxy for relevance. Agents build understanding incrementally, maintaining only necessary context in working memory.

**Tradeoff:** runtime exploration is slower than pre-computed retrieval. Requires well-designed tools and heuristics, or agents waste context on dead ends.

---

### Three Strategies for Long-Horizon Tasks

**Strategy 1: Compaction**

When context approaches the window limit, summarize the conversation and reinitialize with the summary. Same agent continues with compressed history.

```
Agent runs → context fills → summarize history → reinitialize context → same agent continues
```

*Tuning approach:* first maximize recall (ensure no critical information is lost), then iterate to improve precision (eliminate redundant content). Safest lightweight compaction: clear old tool call results — once a tool has been called and its result processed, the raw output no longer needs to occupy context.

*Limitation:* compaction does not give the agent a genuinely clean slate. Does not resolve context anxiety (see Article 6).

**Strategy 2: Structured Note-Taking**

Agent regularly writes key state to external memory files (outside the context window). Notes are retrieved into context as needed.

```
Agent works → writes notes to external file → context resets → agent reads notes → continues
```

*Claude plays Pokémon case:* across thousands of game steps, the agent maintained precise progress tracking — "for the last 1,234 steps I've been training in Route 1, Pikachu has gained 8 levels toward target of 10." After context resets, it read its own notes and continued multi-hour sequences with no prompting on how to organize memory. Maps of explored regions, combat strategies, achievement logs — all self-organized.

*Best for:* iterative development tasks with clear milestones.

**Strategy 3: Sub-Agent Architecture**

Lead agent maintains high-level plan with clean context. Specialized subagents handle focused tasks in their own clean context windows, exploring extensively, then returning only distilled summaries.

```
Lead Agent (clean context, high-level coordination)
    ↓
Subagents (deep exploration, own context windows)
    ↓ return 1,000–2,000 token summaries
Lead Agent synthesizes (context stays uncontaminated)
```

*Best for:* tasks requiring parallel exploration of independent directions.

**Choosing between the three:**

| Task characteristic | Strategy |
|---|---|
| Needs conversational continuity, heavy back-and-forth | Compaction |
| Has clear milestones, iterative development | Structured note-taking |
| Needs parallel independent exploration | Sub-agent architecture |

The three are not mutually exclusive — production systems commonly combine all three.

---

### Conclusion Principle

The guiding principle across all context components: find the smallest set of high-signal tokens that maximizes the probability of the desired outcome. As models become more capable, they require less prescriptive engineering — but treating context as a precious, finite resource remains foundational regardless of model capability.

---

## Article 4 — Building Agents with the Claude Agent SDK
**Published:** Sep 29, 2025
**URL:** https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk

### The Renaming and What It Signals

The Claude Code SDK has been renamed the **Claude Agent SDK**. The reason is architectural, not cosmetic:

Over the preceding months, the harness that drives Claude Code had come to power research, video creation, note-taking, and virtually all of Anthropic's major internal agent loops — far beyond coding. The rename reflects a formal claim: **the harness is general-purpose**. Its value is not "helping Claude write code" but "giving Claude a computer, so it can work like a human."

**Core design principle:** give your agent the same tools a human knowledge worker uses — bash, file read/write, search, code execution. With these primitives, an agent can handle any digital work, not just software development.

---

### The Agent Loop: Three-Stage Framework

This is the central architectural pattern of the SDK, derived from how Claude Code actually operates:

```
┌─────────────────────────────────────┐
│            Agent Loop               │
│                                     │
│  1. GATHER CONTEXT                  │
│     File system / Semantic search / │
│     Subagents / Compaction          │
│            ↓                        │
│  2. TAKE ACTION                     │
│     Tools / Bash / Code gen / MCP   │
│            ↓                        │
│  3. VERIFY WORK                     │
│     Rules / Visual / LLM judge      │
│            ↓                        │
│     Repeat until task complete      │
└─────────────────────────────────────┘
```

---

### Stage 1: Gather Context

**File system as context engineering**

The file system represents information that *could* be loaded into context. When encountering large files (logs, uploads), the agent decides how to load them using bash commands like `grep` and `tail`. The folder and file structure of an agent's environment *is itself* a form of context engineering — naming conventions, directory hierarchy, and timestamps all provide signals the agent can interpret.

*Example:* an email agent stores past conversations in a `Conversations/` folder. When asked about them, it searches that folder rather than loading all history into context upfront.

**Semantic search vs. file system search**

Semantic search (vector retrieval) is faster but less accurate, harder to maintain, and less transparent. File system search (agentic search) is more accurate and fully auditable — you can see exactly what the agent found and why. Default recommendation: start with file system search. Add semantic search only if faster retrieval or variation handling is specifically needed.

**Subagents in the context-gathering stage**

Two distinct values:
1. *Parallelization* — multiple subagents explore different directions simultaneously.
2. *Context isolation* — each subagent uses its own context window and returns only relevant excerpts, not its full context. Ideal for tasks requiring sifting through large information volumes where most content will be irrelevant.

**Compaction**

Built into the SDK: automatically summarizes previous messages when context approaches its limit. Prevents context exhaustion without manual intervention. Based on Claude Code's `/compact` slash command.

---

### Stage 2: Take Action

**Tools — primary execution building blocks**

Tools are the primary actions the agent considers when deciding how to proceed. They occupy prominent space in the context window, meaning every tool definition consumes context budget and shapes what actions the model considers. Design implication: only include tools the agent genuinely needs for its core, frequent actions. A bloated toolset wastes context and creates selection ambiguity.

**Bash & scripts — general-purpose flexibility**

Bash provides a universal capability layer for tasks that don't fit predefined tools. An agent can write code dynamically, execute it, observe results, and iterate — all within a single tool call. This is how Claude handles tasks it wasn't specifically tooled for.

**Code generation — precise, composable, reusable**

Code is the ideal output for complex operations requiring reliability. Consider which tasks would benefit from being expressed as code rather than direct actions — the answer often unlocks significant new capability. Claude.ai's file creation feature (Excel, PowerPoint, Word) relies entirely on Claude writing Python scripts, ensuring consistent formatting and complex functionality.

**MCP — standardized external integrations**

Model Context Protocol provides standardized connections to external services (Slack, GitHub, Google Drive, Asana) with authentication and API calls handled automatically. No custom integration code or OAuth management required. The growing MCP ecosystem means new capabilities can be added as pre-built integrations.

---

### Stage 3: Verify Work

The most commonly neglected stage — and the one most responsible for unreliable agent output.

**Method 1: Rules-based verification**

Provide explicitly defined rules, then explain which rule failed and why. Code linting is the canonical example — TypeScript + linting is stronger than pure JavaScript because it adds multiple independent feedback layers. Best for: any output with formal, enumerable correctness criteria.

**Method 2: Visual feedback**

For visual tasks (UI generation, rendered documents), screenshots provide concrete verification. Using Playwright MCP, agents can automate visual feedback loops — screenshot rendered HTML, test different viewports, verify interactive elements. Check dimensions: layout, styling, content hierarchy, responsiveness.

Best for: outputs with visual presentation that must match a specified design or layout.

**Method 3: LLM as a judge**

A separate language model evaluates the output against fuzzy criteria. Explicitly noted as "not a very robust method" with heavy latency tradeoffs — a last resort for cases where any performance improvement justifies the cost.

Best for: free-text outputs where formal rules and visual inspection are inapplicable.

**Selection logic:**

| Output type | Verification method |
|---|---|
| Has formal correctness criteria | Rules-based |
| Has visual presentation | Visual feedback |
| Free-text with fuzzy quality criteria | LLM as a judge |

---

### Improving an Agent: Diagnostic Questions

After running the loop several times, evaluate through the lens of tool adequacy:

- Agent misunderstands the task → possibly missing key information. Can search API structure be changed to surface what it needs?
- Agent repeatedly fails at a specific task → can a formal rule be embedded in tool calls to identify and fix the failure?
- Agent cannot fix its errors → does it need more creative or flexible tools to approach the problem differently?
- Performance varies as features are added → build a representative test set for programmatic evaluations based on real usage patterns.

---

## Article 5 — Effective Harnesses for Long-Running Agents
**Published:** Nov 26, 2025
**URL:** https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents

### The Core Problem

Even with the Claude Agent SDK and compaction, a frontier model like Opus 4.5 given a single high-level prompt ("build a clone of claude.ai") will fail to produce a production-quality application across multiple context windows. Compaction alone is insufficient.

The structural challenge: long-running agents work in discrete sessions, and each new session begins with no memory of what came before. Like a software project staffed by engineers working in shifts, where each new engineer arrives with no memory of the previous shift.

---

### Two Failure Modes

**Failure mode 1: Attempting too much at once**
Agent tries to implement the entire application in a single pass. Context exhausts mid-implementation, leaving a feature half-built and undocumented. Next agent must guess what happened, spending substantial time just getting the application running again. This occurs even with compaction, which doesn't always pass perfectly clear instructions to the next agent.

**Failure mode 2: Premature completion declaration**
Later in a project, an agent session looks around, sees that progress has been made, and declares the entire project complete — even with significant features unbuilt.

---

### Solution: Two-Agent Structure

```
FIRST RUN
    ↓
Initializer Agent
├─ Writes init.sh (script to start development server)
├─ Creates feature_list.json (all features, all initially "passes": false)
├─ Creates claude-progress.txt (progress log)
└─ Makes initial git commit

EVERY SUBSEQUENT RUN
    ↓
Coding Agent
├─ Reads claude-progress.txt + git log (understand current state)
├─ Reads feature_list.json (identify next uncompleted feature)
├─ Reads init.sh + starts development server
├─ Runs basic end-to-end test (catch any undocumented bugs from last session)
├─ Implements one feature
├─ Tests end-to-end via browser automation (Puppeteer MCP)
├─ git commit with descriptive message
└─ Updates claude-progress.txt
```

Note: these are called separate "agents" only because they have different initial prompts. System prompt, toolset, and harness are otherwise identical.

---

### Three Environment Components

**1. Feature List (feature_list.json)**

The Initializer Agent expands the user's prompt into a comprehensive feature file. In the claude.ai clone example: over 200 features, each described with navigation steps for testing, all initially marked `"passes": false`.

*Why JSON, not Markdown:* after experimentation, models are less likely to inappropriately modify or overwrite JSON files than Markdown files. Coding agents are given an explicit hard constraint: only change the `passes` field value. Cannot delete tests, cannot edit test descriptions. Rationale: "It is unacceptable to remove or edit tests because this could lead to missing or buggy functionality."

**2. Incremental Progress**

Each Coding Agent session implements exactly one feature. This directly addresses the tendency to attempt everything at once. After implementation, the agent must commit to git with a descriptive commit message and write a progress summary. Git history provides a recovery mechanism — if subsequent work breaks something, the agent can revert to a known good state.

**3. Testing (end-to-end, not unit)**

Observed failure mode: agents would make code changes, run unit tests or `curl` commands, and mark features complete — without verifying the feature worked end-to-end from a user's perspective. Solution: require browser automation testing (Puppeteer MCP) on every feature, simulating real user interactions. This dramatically improved performance — agents could identify and fix bugs invisible from code inspection alone.

*Known limitation:* browser automation tools cannot see browser-native alert modals through Puppeteer MCP. Features relying on such modals showed consistently higher bug rates.

---

### Session Startup Protocol

Every Coding Agent session follows a fixed startup sequence:

1. `pwd` — confirm working directory
2. Read `claude-progress.txt` + `git log --oneline -20` — understand recent history
3. Read `feature_list.json` — identify next highest-priority failing feature
4. Read `init.sh` + start development server
5. Run basic end-to-end test — confirm previous session left app in working state
6. Begin implementing selected feature

This startup protocol eliminates context wasted on orientation and catches undocumented regressions before new development begins.

---

### Failure Mode / Solution Table

| Problem | Initializer Agent | Coding Agent |
|---|---|---|
| Agent declares victory too early | Creates feature list with all features initially failing | Reads feature list at session start; selects one uncompleted feature |
| Agent leaves environment with bugs or undocumented state | Creates initial git repo and progress file | Reads progress + git log at start; runs basic test; ends with commit + progress update |
| Agent marks features done without proper testing | Creates feature list | Self-verifies all features via browser automation before marking passing |
| Agent wastes time figuring out how to run the app | Writes init.sh | Reads init.sh at session start |

---

### Open Questions Acknowledged

- Whether a single general-purpose coding agent or a multi-agent architecture (testing agent, QA agent, code cleanup agent) produces better results across sessions remains unresolved.
- The approach is optimized for full-stack web app development. Generalization to scientific research or financial modeling is a stated future direction.

---

## Article 6 — Harness Design for Long-Running Application Development
**Published:** Mar 24, 2026
**URL:** https://www.anthropic.com/engineering/harness-design-long-running-apps

### Starting Point: Two Residual Problems

Building on Article 5's two-agent structure, two problems remained unsolved:

**Problem 1: Context Anxiety**

Some models begin wrapping up work prematurely as they approach what they believe is their context limit — even when there is substantial work remaining. This behavior is called *context anxiety*.

Compaction does not solve it: after compaction, the same agent continues running and still "knows" it has been running for a long time. Behavioral modification persists.

Context Reset solves it: completely clear the context window, start a new agent instance, transfer state via a structured handoff artifact. The new agent has no awareness of prior session length and begins with full capacity.

```
Compaction:
Same agent → compressed history → continues
(still "feels" the accumulated run time)

Context Reset:
Old agent ends → writes handoff artifact → new agent starts fresh
(genuinely clean slate; handoff quality is critical)
```

**Problem 2: Self-Evaluation Bias**

When asked to evaluate their own work, agents consistently praise it — even when output quality is obviously mediocre to human observers. This is most severe for subjective tasks (design), but also present in verifiable tasks.

Key insight: tuning a *separate* evaluator to be skeptical is far more tractable than making a generator critical of its own work. Once external feedback exists, the generator has something concrete to iterate against.

---

### Core Inspiration: GAN Architecture

Generative Adversarial Networks (GANs) separate generation from discrimination into two agents with opposing objectives. Applied to agent harness design:

```
GAN:
Generator ←→ Discriminator (adversarial training)

Harness:
Generator Agent ←→ Evaluator Agent (feedback loop)
```

The Evaluator is explicitly calibrated to be skeptical — its default posture is to find problems, not validate success.

---

### Experiment 1: Frontend Design

**Four scoring dimensions (given to both Generator and Evaluator):**

- **Design Quality** — does the design feel like a coherent whole? Do colors, typography, layout, imagery combine to create a distinct mood and identity?
- **Originality** — is there evidence of custom decisions, or are template layouts, library defaults, and AI-generated patterns visible? Does it exhibit the telltale signs of AI generation (purple gradients over white cards)?
- **Craft** — technical execution: typography hierarchy, spacing consistency, color harmony, contrast ratios. A competence check, not a creativity check.
- **Functionality** — usability independent of aesthetics. Can users understand the interface, find primary actions, and complete tasks without guessing?

Design Quality and Originality were weighted higher. Claude's baseline Craft and Functionality are already adequate. The evaluation pressure needed to drive aesthetic risk-taking, not technical competence.

**Loop mechanics:**
- Generator creates HTML/CSS/JS based on user prompt
- Evaluator receives Playwright MCP — navigates the live page, screenshots it, studies it in detail before scoring
- Evaluator scores each dimension, writes detailed critique
- Critique flows back to Generator as input for next iteration
- 5–15 iterations per generation
- Generator makes strategic decision after each evaluation: refine current direction (scores trending well) or pivot to entirely different aesthetic (approach not working)

**Key findings:**
- Scores generally improved over iterations but not linearly — middle iterations sometimes outperformed the final
- Implementation complexity increased across rounds as Generator reached for more ambitious solutions
- Prompt wording in scoring criteria shaped output character in unexpected ways: "the best designs are museum quality" pushed toward a particular visual convergence
- First iteration was already better than a no-prompting baseline, suggesting the criteria language itself steered the model before any evaluator feedback

**Notable result:** Dutch art museum website. Iterations 1–9: polished dark-themed landing page, visually clean but conventional. Iteration 10: complete pivot — a spatial experience rendered in CSS perspective with a 3D room, checkered floor, artwork hung on walls in free-form positions, doorway-based navigation between gallery rooms. Creative leap not seen in any single-pass generation.

---

### Experiment 2: Full-Stack Development — Three-Agent Architecture

**Planner**

Takes a 1–4 sentence user prompt and expands it into a complete product specification. Prompted to be ambitious about scope. Deliberately focuses on product context and high-level technical design — NOT detailed implementation specifics.

*Rationale:* if the Planner gets a technical detail wrong, that error cascades into the Generator's implementation. Better to constrain what is produced and let downstream agents determine how to produce it. Planner was also given access to the frontend design skill and asked to look for opportunities to weave AI features into the spec.

*Result on "2D retro game maker" prompt:* Planner expanded it into 16 features across 10 sprints, including sprite animation system, behavior templates, sound effects, AI-assisted sprite generator and level designer, and game export with shareable links.

**Generator**

Works in sprints, selecting one feature from the spec at a time. Tech stack: React + Vite + FastAPI + SQLite (later PostgreSQL). Self-evaluates at end of each sprint before handing to Evaluator. Has git for version control.

**Evaluator**

Uses Playwright MCP to interact with the running application as a real user would — testing UI features, API endpoints, database states. Scores each sprint against four criteria (product depth, functionality, visual design, code quality). Hard threshold per criterion: if any criterion falls below threshold, sprint fails and Generator receives detailed feedback for revision.

**Sprint Contract mechanism:**
Before each sprint, Generator and Evaluator negotiate what "done" looks like before any code is written:
1. Generator proposes what it will build and how success will be verified
2. Evaluator reviews the proposal, ensuring Generator is building the right thing
3. The two iterate until agreement is reached
4. Generator builds against the agreed-upon contract
5. Evaluator tests against the contract

Communication is file-based: one agent writes a file, the other reads it and responds within that file or via a new file. This keeps work faithful to the spec without over-specifying implementation details upfront.

---

### Context Reset vs. Compaction: Final Decision Framework

| Condition | Approach |
|---|---|
| Model exhibits context anxiety (premature task wrap-up) | Context Reset — structured handoff artifact between agent instances |
| Model handles long context gracefully | Compaction — SDK automatic compaction handles context growth |

In the Article 5 harness (Sonnet 4.5): context anxiety was strong enough that context resets were essential. In this article's harness (Opus 4.5): context anxiety was largely absent, so automatic SDK compaction was sufficient — the entire build ran as one continuous session.

**The right choice depends on your specific model's behavior, not a universal rule.**

---

### Cost Reality Check

| Configuration | Duration | Cost |
|---|---|---|
| Solo agent | 20 minutes | $9 |
| Three-agent harness | 6 hours | $200 |

20× cost difference. Solo agent output: visually functional but broken game runtime — entity definitions and game runtime wiring disconnected, no surface indication of failure. Three-agent output: 16-feature application with working game engine, AI-assisted tools, and export functionality.

The cost premium is only justified when task value is commensurately high.

---

## Cross-Article Summary: The Full Narrative Arc

```
Article 1 (Dec 2024) — Conceptual Foundation
  Workflow vs. Agent distinction
  Five coordination patterns
  ACI principle
        ↓
Article 2 (Jun 2025) — Multi-Agent in Production
  Lead + Subagent parallel compression model
  Performance data: 90.2% improvement, 15× token cost
  Evaluation and production engineering
        ↓
Article 3 (Sep 2025) — Why Context Is the Core Problem
  Context rot + n² mechanism
  Three long-horizon strategies
  Just-in-time vs. static retrieval
        ↓
Article 4 (Sep 2025) — SDK and Agent Loop Framework
  Claude Agent SDK: harness is general-purpose
  Three-stage loop: Gather → Act → Verify
        ↓
Article 5 (Nov 2025) — Cross-Context-Window Engineering
  Initializer + Coding Agent two-agent structure
  File system as inter-session state medium
  Incremental progress + end-to-end testing
        ↓
Article 6 (Mar 2026) — Self-Evaluation and Architectural Maturity
  GAN-inspired Generator-Evaluator separation
  Three-agent: Planner + Generator + Evaluator
  Sprint Contract for pre-implementation alignment
  Context Reset for context anxiety
```

**The through-line:** the series progressively surfaces one production challenge at a time — pattern selection, coordination at scale, context limits, tooling, cross-session continuity, self-evaluation bias — and provides engineering solutions that build directly on each other. Each article assumes the engineering of the previous ones and extends it.

**The constant principle across all six:** complexity is a cost, not a virtue. Add it only when it demonstrably solves a problem the simpler approach cannot.
