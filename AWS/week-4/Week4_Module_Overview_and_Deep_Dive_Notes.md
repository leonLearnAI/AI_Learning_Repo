# Module 11: Bedrock Core Services and Mechanisms (7 items)

## 11.1 Overview of All 7 Items

### ★★★ Converse API
**Bedrock's unified calling interface**

*(Covered in depth this week on Day 22 — see section 11.2 below; omitted here.)*

### ★★★ Tool Use (function calling)
**The underlying mechanism behind agents**

*(Covered in depth this week on Day 24 — see section 11.2 below; omitted here.)*

### ★★★ Model selection methodology
**The capability / latency / cost triangle**

*(Covered in depth this week on Day 23 — see section 11.2 below; omitted here.)*

### ★★★ The four billing modes
**On-Demand / Provisioned Throughput / Batch Inference / Prompt Caching**

*(Covered in depth this week on Day 23 — see section 11.2 below; omitted here.)*

### ★★☆ Cross-Region Inference Profile
**Automatic multi-region routing, with a compliance side effect**

*(Covered in depth this week on Day 23 — see section 11.2 below; omitted here.)*

### ★★☆ The four model customization methods
**Fine-tuning / continued pre-training / distillation / custom model import**

When a pre-trained foundation model can't fully meet a business need, there are four "customization" levers, each solving a different problem: **fine-tuning** uses a small amount of labeled data to adjust the model's output style or format; **continued pre-training** uses a large volume of unlabeled domain-specific text to fill in knowledge gaps in a particular domain; **distillation** uses a stronger, larger model to "teach" a smaller model, letting the small model approach the larger one's performance on a specific task at lower cost; **custom model import** brings a model you trained elsewhere directly into Bedrock for unified management and invocation. The typical decision order is: first see if prompt engineering can solve it (cheapest) → if not, consider RAG (adds knowledge, dynamic) → if still not enough, consider fine-tuning (changes style/format) or continued pre-training (adds domain knowledge) → finally consider distillation to cut cost. **This is also the comparison most often paired with prompt engineering and RAG as a confusion set**: change behavior → prompt engineering; add knowledge → RAG (dynamic); change style/format → fine-tuning (needs labeled data); add domain knowledge → continued pre-training (needs massive unlabeled text); cut cost → distillation.

**Example**: A company wants its customer service model to sound more like its brand's voice. They fine-tune on a small set of labeled historical support conversations so the model learns that particular tone, rather than retraining a model from scratch or undertaking the much heavier work of continued pre-training.

### ★★☆ Bedrock's data usage commitment
**Inputs and outputs are never used to train the foundation models**

*(Covered in depth this week on Day 22 — see section 11.2 below; omitted here.)*

## 11.2 This Week's Deep Dive: Converse API, Model Selection/Billing, and Tool Use (Day 22–24)

**① Bedrock core and the Converse API (Day 22)**
- Bedrock is "renting," not "self-hosting" — it fully manages model deployment and operations, trading a per-call price for not having to run any of that infrastructure yourself.
- **Learn only Converse, not the older InvokeModel** — Converse uses a unified request format that abstracts away the differences between model families; switching models just means changing the `modelId`.
- A single call has three parts: **messages** (conversation history — the model has no memory, so "remembering" comes entirely from resending it each time), **system** (a separate role/persona setting), and **inferenceConfig** (generation parameters).
- Three inference parameters: **temperature** (overall randomness), **top_p** (defines a candidate pool based on cumulative probability, not a fixed count), **max_tokens** (a hard length cap).
- **ConverseStream**: the streaming variant, returning a series of events (message start / content deltas / message stop); the backend forwards each delta as it arrives to produce a typewriter effect.
- **Data usage commitment**: inputs and outputs are never used to train the foundation models — almost always the first question a customer asks.

**② Model selection and the four billing modes (Day 23)**
- Capability, latency, and cost are always in tension — start from how much capability the task actually needs, don't default to the strongest model.
- Output tokens cost 3–5x more than input tokens, because generation is sequential, token-by-token computation, while reading input can be processed in parallel.
- Four billing modes: **On-Demand** (unpredictable usage), **Provisioned Throughput** (steady high volume, and the *only* entry point for custom models), **Batch Inference** (offline work, roughly half price), **Prompt Caching** (fixed prefix + high-frequency calls, big discount via prefix matching).
- Cross-Region Inference Profiles improve availability but carry a data-residency compliance side effect — European customers in particular need the routing scope confirmed first.
- The cost impact of context length **grows faster than linearly** — which is also why "retrieving only what's relevant" beats "stuffing in everything."

**③ Tool Use / function calling (Day 24)**
- The model itself can't "act" — it can only "accurately state what help it needs."
- The full round trip has four steps: send the tool list → model issues a structured tool-call request → your code actually executes it → the result (or error) is fed back to the model → the model generates the final answer based on that result.
- **How well the tool's description is written directly determines whether the model uses it correctly** — fundamentally a semantic-matching problem.
- Independent tool calls can run in parallel; calls with a dependency must run sequentially.
- When a tool call fails, the error also needs to be honestly fed back to the model (not have your code compose the user-facing response itself) — otherwise the model either stalls or hallucinates.
- **Tool Use is the foundation of agents** — an agent is simply this "call a tool → see the result → decide the next step" loop run over and over.

## 11.3 Architecture / Flow Diagrams (Described in Text)

**Structure of a single Converse call**
```
messages (conversation history) + system (persona) + inferenceConfig (temperature/top_p/max_tokens)
→ sent to the Converse API → model generates a reply
(for streaming, use ConverseStream instead, which returns an event stream the backend forwards to the frontend as it arrives)
```

**The full Tool Use round trip**
```
① send the tool list + user question to the model → ② model decides it needs a tool, issues a structured call request
→ ③ your code actually executes it (calling a database/external API) → ④ the result (or error) is fed back to the model
→ the model generates the final natural-language answer based on that result
```

---

# Module 12: Bedrock Sub-services (7 items)

## 12.1 Overview of All 7 Items

### ★★★ Knowledge Bases
**Managed RAG**

*(Covered in depth this week on Day 25–26 — see section 12.2 below; omitted here.)*

### ★★★ Guardrails
**Real-time guardrails on LLM input and output**

*(Covered in depth this week on Day 27 — see section 12.2 below; omitted here.)*

### ★★★ AgentCore
**Production infrastructure for agents — framework-agnostic, model-agnostic**

*(Covered in depth this week on Day 29 — see section 12.2 below; omitted here.)*

### ★★☆ Bedrock Evaluations
**Automated evaluation / human evaluation / LLM-as-a-judge**

*(Covered in depth this week on Day 30 — see section 12.2 below; omitted here.)*

### ★★☆ Prompt Management
**Versioning and centralized management for prompts**

Prompt Management lets you pull prompts out of your code and manage them centrally, with support for version control (comparing the effect of different versions, rolling back at any time) and variable placeholders (the same prompt template filled with different values at runtime) — avoiding prompts scattered as hardcoded strings throughout the codebase that require a search-and-replace across the whole repo every time they change.

**Example**: A team's customer-service chatbot prompt needs frequent iteration. Previously, changing the prompt meant changing code and redeploying; with Prompt Management, prompts are versioned and released independently, and business staff can test new prompt versions without an engineer's involvement.

### ★★☆ Prompt Flows
**Visual orchestration for lightweight workflows**

Prompt Flows provides a drag-and-drop visual interface for chaining together multiple prompt calls, conditional branches, and data transformations like a flowchart — no need to write a full Step Functions state machine or hand-roll glue code for what's really a fairly simple multi-step prompt sequence.

**Example**: A team wants to build a two-step flow — "first classify the user's intent, then call a different prompt template based on that intent to generate the reply." With Prompt Flows they drag a few nodes together to build it, with no code required.

### ★★☆ Amazon S3 Vectors
**Object storage with native vector support — one of the cheapest options for RAG**

> ⚠️ This item was a genuine content gap discovered during the Day 30 comprehensive review, when cross-checking the "four vector-store options" confusion pair — it was never covered anywhere in the 30-day plan, and is added here to close that gap.

S3 Vectors is the world's first cloud object storage service with **native support for storing and querying vectors**, reaching general availability in late 2025. It adds a new "vector bucket" bucket type to S3, along with a dedicated set of APIs for storing and querying vectors — no infrastructure to provision. Its core selling point is **cost**: compared to conventional vector-store approaches (like OpenSearch), it can reduce storage and query costs by up to 90%, essentially layering vector-search capability on top of S3's existing "cheap, massive-scale, zero-ops" characteristics. At scale, a single index can hold up to 2 billion vectors; on performance, it's somewhat slower than a purpose-optimized search engine like OpenSearch (query latency starts around 100ms, with infrequent queries returning within a second). It integrates natively with **Bedrock Knowledge Bases** and can serve directly as its vector-store backend, and can also be paired with OpenSearch in a **tiered strategy** — massive, infrequently accessed data goes in S3 Vectors to save money, while the portion needing high-performance real-time queries goes in OpenSearch.

**Example**: A company wants to give an agent "long-term memory" — storing a massive volume of historical interactions, documents, and insights. Storing all of that in OpenSearch would make costs scale linearly with data volume; switching to S3 Vectors lets them store billions of vectors at very low cost, so the agent isn't forced to "forget" old context.

## 12.2 This Week's Deep Dive: Knowledge Bases, Guardrails, and AgentCore (Day 25, 27, 29–30)

**① Knowledge Bases and chunking (Day 25)**
- Full pipeline: data source → ingestion (chunking + embedding generation) → vector store → retrieval → (optional) generation.
- **Four chunking strategies**: fixed-size (simple and blunt), semantic (splits at topic shifts), hierarchical (follows the document's natural structure), custom Lambda (handles special formats).
- Chunks too small lose context; too large dilutes semantics. **Overlap** is the safety net for "information lost right at a split point."
- **Retrieve** (you assemble the prompt yourself, full control) vs. **RetrieveAndGenerate** (one step, but a black box) — anything needing custom assembly logic must use the former.
- **Metadata filtering** handles multi-tenant isolation and time-relevance constraints; **reranking** balances speed and accuracy via a two-stage "coarse recall, then fine ranking" design.

**② Guardrails and prompt safety (Day 27)**
- Five capabilities: **content filters** (a universal safety baseline), **denied topics** (business boundaries, unrelated to whether content is harmful), **sensitive information masking** (configured on both input and output sides, protecting against different risks), **contextual grounding checks** (real-time hallucination interception — the runtime counterpart to the Day 26 faithfulness metric, solving the same problem at a different point in time), **automated reasoning checks** (validation against hard, formal logical rules).
- Three prompt-injection techniques: direct instruction override, role-play bypass, and **indirect injection** (hidden in external content — especially worth watching for in agent scenarios).
- Defense can't rely on Guardrails alone — layer in stronger system-prompt language, least-privilege for tools, human approval, and contextual grounding checks together.
- Guardrails (the live model call path) vs. Comprehend (a general-purpose text analysis tool) vs. Macie (scanning static data in S3) — these three differ in *where* they operate.

**③ AgentCore and production readiness (Day 29)**
- Seven components: **Runtime** (dedicated long-running hosting for agents), **Gateway** (automatically turns existing APIs into MCP tools), **Memory** (managed session and long-term memory), **Identity** (properly scoping credentials and permissions when an agent acts on behalf of a specific user calling downstream systems), **Observability** (an X-Ray equivalent built for multi-turn looping execution paths), **Evaluations** (continuous quantitative tracking of an agent's behavioral quality), **Policy** (Cedar-based, governs whether an action is allowed at the business level).
- IAM governs "can this identity touch this AWS resource"; Policy governs "can this agent take this business action in this context" — the two can coexist, with different jurisdictions.
- Bedrock Agents (turnkey but tied to the Bedrock ecosystem) vs. AgentCore (framework-agnostic and model-agnostic, but requires more assembly).

**④ Bedrock Evaluations' three modes (Day 30)**
- **Automated evaluation** (fast early-stage iteration, only works for scenarios with a clear correct answer), **human evaluation** (a thorough quality gate before launch — closest to real user perception, but slow and expensive), **LLM-as-a-judge** (continuous, large-scale monitoring after launch — sits between the other two).
- LLM-as-a-judge's biases: preference for longer answers, and position bias (order affects scoring) — mitigated with explicit instructions, averaging over swapped orderings, and periodic human spot-checks.

## 12.3 Architecture / Flow Diagrams (Described in Text)

**The full Knowledge Bases pipeline**
```
Data source → ingestion (chunking → generating embeddings) → vector store
→ retrieval (the user's question is turned into a vector, then an approximate nearest-neighbor search is run)
→ (optional) generation: Retrieve returns raw fragments for you to assemble / RetrieveAndGenerate does it in one step
```

**A troubleshooting approach for "it got the answer wrong"**
```
First check whether the correct answer actually appears in this query's retrieved content
→ nothing relevant was retrieved: the problem is in retrieval (couldn't find it / found the wrong thing)
→ the right content was retrieved but the answer is still wrong / unused: the problem is in generation (retrieved but not used / context too long and diluted)
```

**Where AgentCore components sit in a production-grade agent's architecture**
```
Agent reasoning logic (Strands or any framework — framework-agnostic)
├─ Runtime: hosts this agent as a long-running process
├─ Gateway: automatically converts the company's existing APIs into MCP tools for the agent to call
├─ Memory: manages session state and long-term memory
├─ Identity: scopes credentials and permissions when the agent acts on behalf of a specific user calling downstream systems
├─ Observability: records the full execution path across multiple reasoning loops
├─ Evaluations: continuously assesses the agent's behavioral quality
└─ Policy (Cedar): fine-grained, business-level authorization decisions
```

---

# Module 13: Other AI Services (10 items)

## 13.1 Overview of All 10 Items

### ★★★ Amazon Textract
**Structured document extraction**

Textract automatically extracts text, tables, and form fields from unstructured documents like scans, images, and PDFs — it's not just simple OCR text recognition; it also understands table row/column structure and the "field name → field value" relationships within forms. This is the core tool for Intelligent Document Processing (IDP) scenarios, and was already mentioned back on Day 17 as the go-to tool for the "text extraction" step of RAG data cleaning.

**Example**: An insurance company needs to process a large volume of scanned paper claim forms. Textract automatically extracts fields like name, policy number, and claim amount, eliminating manual data entry.

### ★★☆ Amazon Comprehend
**A general-purpose NLP API, including PII detection**

*(Already covered when discussing Guardrails/Comprehend/Macie's division of labor on Day 27 — not repeated here. Key takeaway: Comprehend is a general-purpose text analysis tool, not exclusive to LLM scenarios — it can be called anywhere text needs analyzing.)*

### ★★☆ Amazon Kendra
**Enterprise-grade semantic search**

Kendra is an out-of-the-box enterprise search engine that connects to multiple data sources (SharePoint, S3, databases, etc.), applies semantic understanding to documents, and provides search over them — returning "the most relevant document fragments," rather than generating a synthesized answer from retrieved content the way Knowledge Bases does. It's more like "a smarter version of your internal search box" than a RAG component.

**Example**: A company wants to build an internal search tool for employees that understands "expense reimbursement process" and "how do I get reimbursed" mean the same thing. Using Kendra, employees search and see links to the most relevant internal documents directly, with no generated summary answer.

### ★★☆ Amazon Q Business
**An out-of-the-box enterprise knowledge assistant**

Amazon Q Business is a no-code, finished enterprise Q&A application. Once connected to your company's various data sources, employees can ask questions in natural language and get synthesized answers — with the RAG retrieval and generation steps already packaged behind the scenes. Compared to building your own RAG system with Knowledge Bases + Bedrock, Q Business eliminates most of the development work, at the cost of lower customization and flexibility.

**Example**: A mid-sized company wants to quickly roll out an assistant employees can ask about company policy, without much engineering bandwidth to build it themselves. They procure Amazon Q Business directly, connect it to internal documents, and have it running within days.

### ★★☆ SageMaker JumpStart
**One-click deployment of open-source models to your own endpoint**

SageMaker JumpStart offers a library of open-source models that you can deploy with one click to your own dedicated inference endpoint, without building model-deployment infrastructure from scratch. Unlike calling an already-hosted model via Bedrock, what JumpStart deploys is "an endpoint that belongs exclusively to you."

**Example**: A team wants to use a specific open-source image classification model without setting up their own GPU servers and inference service. With JumpStart, a few steps deploy the model into a callable API endpoint.

### ★★☆ SageMaker Model Monitor / Clarify / Model Registry
**A monitoring, explainability, and version-management trio for traditional ML models**

These three tools serve the "training/deploying your own traditional machine-learning model" track, and have little to do with generative AI, but the exam scope calls out the distinction: **Model Monitor** continuously watches whether a production model's performance is "drifting" (the input data distribution no longer matches what it was trained on, degrading performance); **Clarify** detects model bias and helps explain why a model made a given decision; **Model Registry** manages different model versions, tracking each version's performance and lineage.

**Example**: A bank uses a traditional ML model to score loan applications. They use Model Monitor to continuously watch whether the model's input data is drifting significantly over time, triggering a retraining process if drift is detected.

### ★★☆ Augmented AI (A2I)
**A human-review loop**

A2I lets you insert a "route low-confidence results to a human reviewer" step into an automated pipeline — for example, when Textract extracts a form and some field's confidence score falls below a threshold, A2I automatically routes that document to a human reviewer to confirm or correct it before it continues downstream, instead of letting an uncertain automated result flow straight into production and cause an error.

**Example**: A company automates ID-card recognition with Textract. When handwriting is blurry and confidence drops below 90%, A2I automatically routes the image to a human reviewer, instead of letting the system trust a potentially incorrect reading.

### ★★☆ Amazon Lex
**A conversational bot framework**

Lex is used to build conversational interfaces (chatbots, voice bots), built around the concepts of "intent" and "slot" — first identifying what the user wants to do (intent), then collecting the specific information needed to do it (slots — e.g., booking a flight needs origin, destination, and date). It's more structured than calling an LLM directly for conversation, and better suited to scenarios with a fixed process flow; it's now also often paired with Bedrock, with Lex handling the process skeleton and the LLM handling the more flexible natural-language understanding.

**Example**: An airline's flight-booking chatbot defines a "book a flight" intent in Lex. Once it recognizes the user wants to book, it collects the origin, destination, and date slots in turn, then calls the backend booking system once all the information is gathered.

### ★☆☆ Transcribe / Polly / Rekognition
**Speech-to-text, text-to-speech, and image recognition trio**

Three relatively mature, traditional AI services: **Transcribe** converts speech to text; **Polly** converts text to natural-sounding speech; **Rekognition** identifies objects, faces, scenes, and text in images/video. In GenAI applications, they often serve as an "input/output conversion layer" alongside an LLM.

**Example**: A voice-based smart customer service system: the user's speech first passes through Transcribe to become text; that text question goes to Bedrock to generate a reply; the reply text then passes through Polly to be spoken back to the user — creating a voice-in, voice-out experience.

### ☆☆☆ SageMaker training-related tools (HyperPod, Processing, Ground Truth, Neo)
**Model-training-related tools (not on the exam — skip)**

HyperPod (managing large-scale distributed training clusters), Processing (data pre-/post-processing jobs), Ground Truth (human data-labeling service), Neo (model compilation optimization for specific hardware) — all serve the "training/optimizing a model from scratch" track. **The AIP-C01 exam explicitly states that model training and advanced ML techniques are out of scope**, so Phase 1 can skip this entirely.

## 13.2 A Note

This module had no dedicated deep dive this week (Day 22–30) — Textract got a brief mention on Day 17, Comprehend was expanded on in Day 27's comparison table, and the rest of these services are appearing here as full entries for the first time. Phase 1 doesn't need to dig into operational details for these yet — just building the "roughly what problem this service solves, and when it should come to mind" level of awareness is enough for now.

---

# Supplement: Non-Product Concepts (RAG Engineering / Prompt Engineering / Agent Engineering / Evaluation & Observability / Responsible AI & Compliance)

This content doesn't map to any specific starred AWS product — the companion document files it separately as "Module C." It's spread across Day 24, 26, 27, 28, and 30, and gathered here.

## C1. RAG Engineering (Day 26)

- **Four evaluation metrics split into two groups**: context recall + context precision (govern the retrieval stage, a see-saw pair with each other), faithfulness + answer relevance (govern the generation stage).
- **Four failure modes**, each mapped to a metric: couldn't retrieve it → low recall; retrieved the wrong thing → low precision; retrieved it but didn't use it → a faithfulness problem; context too long and diluted → can hurt both faithfulness and relevance at once.
- **Troubleshooting order**: first check whether the correct answer is present in what was retrieved this time, to decide whether to dig into retrieval or generation — don't re-test the entire pipeline from scratch every time.
- Citation/source attribution isn't an evaluation metric — it's a chain of evidence the user can verify themselves for faithfulness, and it's essentially required in enterprise scenarios.

## C2. Prompt Engineering (scattered across Day 22–27)

- Structured output (getting the model to reliably return a fixed format, like JSON), and the division of labor between the system prompt and user prompt (Day 22 covered why `system` and `messages` are kept separate).
- Prompt versioning and iteration (maps to the Prompt Management product, see 12.1).
- Prompt injection and defense belong to the security domain and were already covered in depth under Guardrails (Day 27).

## C3. Agent Engineering (Day 28)

- **The reasoning loop (ReAct)**: repeatedly runs the Tool Use round trip across multiple turns, with the model itself deciding when it has "enough" to give an answer.
- **Short-term memory** relies on resending the conversation history (within this one conversation); **long-term memory** relies on external storage + retrieval (across conversations) — two mechanisms solving problems at different time scales.
- **MCP**: the standardized protocol for tool integration, solving the "every framework needs its own re-adaptation of each tool" duplication problem — think of it as a "standard outlet."
- **Multi-agent patterns**: Supervisor-Worker (a manager dispatches tasks), Workflow (a relay with a fixed order), Graph (a more complex relay network with branches and merges), Swarm (no central coordinator, self-organizing) — complexity and controllability decrease along this spectrum while flexibility increases.
- **When not to use an agent**: when the flow can be fully enumerated ahead of time, when strict, repeatable accuracy is required, or when extreme speed and concurrency are needed — all three belong to Step Functions.
- Three forms of agent failure: infinite loops (cap the maximum number of turns), tool misuse, and privilege escalation (ties back to AgentCore's Identity/Policy).

## C4. Evaluation and Observability (Day 30 + earlier weeks)

- An evaluation set should start with 20–50 questions, covering typical scenarios, edge cases, and scenarios that should be refused — and should keep growing as new failure cases come up post-launch.
- LLM-as-a-judge's two systematic biases (favoring longer answers, position bias) and the corresponding mitigations.
- LLM-specific observability metrics (tying back to Day 19): TTFT, token usage, cost attribution, refusal rate — these can now be understood as things the Bedrock Evaluations and Observability components jointly track.

## C5. Responsible AI and Compliance (Day 30)

- **Six dimensions**: fairness, explainability (maps to citation/source attribution), privacy and security (maps to Guardrails' PII masking), robustness (holding up against attacks like prompt injection), governance (needs the evaluation sets, observability, and Evaluations tools discussed above to back it up), transparency (letting users know they're interacting with AI).
- **Three-way responsibility split**: the model producer (training data quality, model safety testing), the model provider (infrastructure security, the data usage commitment, providing tools like Guardrails), and the model consumer (that's you — is this the right scenario, have you added safeguards, are you accountable for the final result).
- **Three questions European customers ask**: data residency (ties to Day 23's Cross-Region Inference Profiles), GDPR (right to be forgotten, data minimization, data processing agreements), the EU AI Act (risk-tiered regulation — the higher the risk tier, the more compliance documentation is required) — in this context, the evaluation reports and observability records discussed today aren't just good engineering practice, they're compliance evidence in their own right.

---

# Supplement: Four Confusion Pairs Identified During the Day 30 Comprehensive Review

The companion document 《AWS学习计划_概念补齐版》's Module D lists 16 confusion pairs in total. 12 of them were already covered thoroughly across the 30 daily lessons (each can be found directly within its corresponding Day). The remaining 4 had each individual service covered on its own, but were never placed side by side for a direct comparison — closing that gap here during the Day 30 comprehensive review, for easier recitation and reference.

## The four vector-store options

| Option | Positioning | Best suited for |
|---|---|---|
| **OpenSearch Serverless** | Most full-featured, best performance, but most expensive (has a minimum OCU billing floor) | Complex retrieval needs (hybrid search, high-frequency real-time queries), budget available |
| **Aurora + pgvector** | Rides on an existing Aurora bill — the best value | Team already uses PostgreSQL/Aurora, moderate data scale |
| **Neptune Analytics** | Graph database + vector capability | GraphRAG scenarios, where the data itself is a complex relationship network |
| **S3 Vectors** | Object storage with native vector support, lowest cost, relatively weaker query performance (latency starts around 100ms) | Extremely large data volumes (billions of vectors), query frequency not especially high, extremely cost-sensitive |

## Knowledge Bases vs. Kendra vs. Amazon Q Business

| | Knowledge Bases | Kendra | Amazon Q Business |
|---|---|---|---|
| What it is | A managed RAG component you assemble yourself in code | An enterprise search engine, returns document fragments | A finished, out-of-the-box Q&A application |
| Requires coding? | Yes | Yes (at minimum, a frontend to call it) | Basically no |
| What it returns | Retrieved fragments, or a synthesized answer after generation | The most relevant document links/fragments, no synthesized answer | A directly generated, synthesized natural-language answer |
| Flexibility | Highest — every step (chunking/retrieval/generation) is customizable | Moderate — mainly customization of search behavior | Lowest — mostly configuration options rather than code-level customization |
| Best suited for | Building a deeply customized RAG application yourself | Just needing "a smarter internal search box" | Wanting to launch quickly without much engineering bandwidth |

## Bedrock Agents vs. AgentCore vs. Step Functions vs. Strands

| | Positioning | Who manages the "reasoning logic" |
|---|---|---|
| **Bedrock Agents** | A managed, turnkey single-agent product | Bedrock manages the entire ReAct loop for you — basically nothing to write yourself |
| **AgentCore** | Production infrastructure for agents (Runtime/Gateway/Memory/Identity, etc.) | Doesn't manage reasoning logic at all — only manages "how this agent runs reliably in production" |
| **Strands Agents** | AWS's open-source agent development framework | Provides the toolkit for writing your own reasoning logic (including multi-agent collaboration patterns) |
| **Step Functions** | Deterministic workflow orchestration | No "reasoning" involved — which branch to take next is decided at design time |

**How they relate**: if the flow can be fully enumerated ahead of time → Step Functions, no agent needed. Need an agent but want a fast, turnkey launch → Bedrock Agents. Need an agent *and* need fine-grained control over the reasoning logic (e.g., a custom multi-agent collaboration pattern) → write the reasoning logic yourself with a framework like Strands, then have AgentCore host that agent's production runtime (the two work together, not either/or).

## Bedrock Evaluations vs. SageMaker Clarify vs. A2I

| | What it evaluates | Best suited for |
|---|---|---|
| **Bedrock Evaluations** | The output quality of a generative model (accuracy, faithfulness, tone) | Evaluating a GenAI application's effectiveness — maps to Day 30's three evaluation modes |
| **SageMaker Clarify** | Bias and explainability in a traditional ML model | A traditional ML model you trained/deployed yourself (e.g., a loan-approval scoring model) |
| **A2I** | Not "evaluation" at all — it's a human-review loop, routing low-confidence results to a human | Any automated pipeline that needs an "if unsure, ask a human" safety net |

**In one line**: Evaluations governs "how well a generative model responds," Clarify governs "whether a traditional ML model's decisions are fair and explainable," and A2I doesn't evaluate anything — it's a "call in a human when uncertain" safety valve built into the pipeline.
