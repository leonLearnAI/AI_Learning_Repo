# Module 7: Application Integration (6 services)

## 7.1 Overview of All 6 Services

### ★★★ AWS Step Functions
**Visual workflow orchestration**

*(Covered in depth this week on Day 16 — see section 7.2 below; omitted here.)*

### ★★☆ Amazon EventBridge
**Event routing bus**

*(Covered in depth this week on Day 15 — see section 7.2 below; omitted here.)*

### ★★☆ Amazon SQS (Simple Queue Service)
**Point-to-point message queue**

*(Covered in depth this week on Day 15 — see section 7.2 below; omitted here.)*

### ★★☆ Amazon SNS (Simple Notification Service)
**One-to-many broadcast notifications**

*(Covered in depth this week on Day 15 — see section 7.2 below; omitted here.)*

### ☆☆☆ Amazon AppFlow
**A bridge for automatic data sync between companies**

AppFlow lets you automatically sync data — bidirectionally, with no code — between AWS services and third-party SaaS applications (Salesforce, Slack, ServiceNow, etc.), with built-in data transformation, field mapping, and filtering, on either a schedule or in real time.

**Example**: A company wants to regularly sync customer data from Salesforce into S3 for analysis. They configure an AppFlow flow that syncs automatically every night, instead of writing scripts to call the Salesforce API themselves.

### ☆☆☆ AWS AppConfig
**Dynamic configuration management and safe rollout**

AppConfig lets you pull application configuration (feature flags, rate-limit thresholds, etc.) out of your code and manage it centrally, with support for gradual rollouts — pushing a new configuration to a small slice of instances first, watching for problems, then expanding gradually, with automatic rollback if something goes wrong. You can change application behavior without redeploying code.

**Example**: A team wants to add a new feature flag. Using AppConfig, they enable it for 5% of users first, watch for errors, then gradually roll it out to 100% — and can roll it back instantly if a problem shows up midway, with no code redeploy needed.

## 7.2 This Week's Deep Dive: Four-Way Queue Selection and Step Functions (Day 15–16)

**① Messaging and event four-way selection (Day 15)**
- **SQS**: a message is processed by exactly one consumer, protected from duplicate pickup by a **visibility timeout**. A failed message **automatically reappears** in the queue for someone else to pick up (so your processing logic needs to be idempotent). Standard queues offer high throughput without ordering guarantees; FIFO queues guarantee order but have limited throughput. Messages that keep failing get isolated in a **dead-letter queue (DLQ)** for later investigation.
- **SNS**: one-to-many broadcast, but **has no retry/buffering capability** — a failed delivery is essentially lost. **SNS fanning out to multiple SQS queues** is the classic combination: SNS fills SQS's "can't do one-to-many" gap, and SQS fills SNS's "can't retry" gap.
- **EventBridge**: adds **content-based conditional routing, a Schema Registry, scheduled triggers, and third-party SaaS integration** on top of what SNS offers — an "SNS with smart routing built in."
- **Kinesis** (technically part of the "Analytics" module, but compared alongside the messaging services this week): its most fundamental difference from the other three is that **data isn't consumed away** — it's retained for a period by default (24 hours, up to 365 days), and multiple consumers can each independently read, and even re-read, the same data. Purpose-built for scenarios where the same data needs to be fully read by multiple parties, potentially replayed.

**② Step Functions (Day 16)**
- Six basic state types: Task (does work), Choice (branching), Wait (pauses), Succeed/Fail (terminal states), **Parallel** (a fixed number of logically different branches running at once), **Map** (the same logic applied across an array of unknown size — for very large volumes, use **Distributed Map**).
- Standard workflows (billed per state transition, exactly-once execution, up to 1 year long, supports human-approval callbacks) vs. Express workflows (billed by execution count + duration + memory, at-least-once execution, capped at 5 minutes, much higher throughput).
- **Human-approval checkpoints** are implemented via the `.waitForTaskToken` callback pattern, **supported only in standard workflows** — because Express's 5-minute cap is fundamentally incompatible with "might have to wait several hours."
- **Step Functions vs. Agent**: if you can fully design out "do this, then that, and take this branch under these conditions" ahead of time → Step Functions (cheap, fast, predictable). If the next step has to be decided by the model on the fly → Agent (expensive, harder to predict, but handles scenarios you can't fully enumerate).

## 7.3 Architecture / Flow Diagrams (Described in Text)

**Parallel vs. Map**
```
Parallel: a fixed number of logically different branches running at once (e.g., "extract text" and "generate a thumbnail" starting together)
Map: the same logic applied to an array of unknown size (e.g., 50 documents, each running through the same processing flow)
```

**State machine: "Upload document → extract → detect PII → generate summary → save"**
```
Task (extract text) → Task (detect PII)
  → Choice: high-sensitivity information detected?
      → Yes: enter callback wait (generate a task token, wait for human approval, continue after SendTaskSuccess)
      → No: proceed directly
  → Task (generate summary) → Task (save to database) → Succeed
```

**SNS fanning out to multiple SQS queues**
```
Publisher → sends one message to SNS → SNS copies it and delivers it to multiple SQS queues subscribed underneath it
→ each queue feeds an independent system (inventory / email / finance), each processing at its own pace and retrying independently on failure
```

---

# Module 8: Analytics (8 services)

## 8.1 Overview of All 8 Services

### ★★★ Amazon OpenSearch Service / Serverless
**The default retrieval backend for RAG**

*(Covered in depth this week on Day 18 — see section 8.2 below; omitted here.)*

### ★★★ AWS Glue
**Data discovery, cataloging, and ETL**

*(Covered in depth this week on Day 17 — see section 8.2 below; omitted here.)*

### ★★☆ Amazon Athena
**Serverless SQL queries over S3**

*(Covered in depth this week on Day 17 — see section 8.2 below; omitted here.)*

### ★★☆ The Kinesis family
**Ordered, replayable data streams**

*(Covered in depth this week on Day 15 — see section 7.2 above; omitted here.)*

### ★★☆ AWS Lake Formation
**Unified permission management for a data lake**

Lake Formation lets you set fine-grained row- and column-level access controls at the data lake layer — for example, "people in this department can only see sales data for their own region" or "these columns contain salary data, visible only to HR" — without configuring permissions separately in every query engine (Athena, Redshift, EMR). You manage it once, centrally, and every query engine respects the same rules.

**Example**: A multinational's data lake holds data from every subsidiary worldwide. Using Lake Formation, they configure "analysts in each region can only query data for their own region," instead of setting permissions separately in every query tool.

### ☆☆☆ Amazon QuickSight
**Cloud-native business intelligence and visualization**

QuickSight is a BI tool for data visualization and dashboards. It connects directly to data sources like S3, Athena, and Redshift, lets you build charts and reports with drag-and-drop, and includes some ML-driven automatic insight features (like automatically flagging unusual spikes in the data).

**Example**: An ops team wants a daily visual dashboard of sales data. Connecting QuickSight to Athena query results, they build an auto-refreshing chart dashboard in minutes, with no engineer needed to write reporting code.

### ☆☆☆ Amazon EMR
**Managed big-data processing clusters**

EMR lets you quickly stand up and manage clusters running big-data frameworks like Hadoop and Spark, suited to workloads that need massively parallel processing of huge datasets — complex data transformations, or large-scale feature engineering ahead of model training.

**Example**: A team needs to clean and transform tens of terabytes of raw log data. They spin up a Spark cluster on EMR to process it in parallel, then shut the cluster down automatically once done, without maintaining a permanently running big-data infrastructure.

### ☆☆☆ Amazon Redshift
**A cloud-native data warehouse**

Redshift is a data warehouse service optimized for large-scale, complex analytical queries, built on columnar storage and massively parallel processing — suited to running complex aggregate analysis over huge volumes of structured data. Compared to Athena (ad hoc queries directly over S3), Redshift is better suited to "data that's already organized and needs repeated, complex analysis over the long term."

**Example**: A retailer loads years of sales data, fully organized, into Redshift. Analysts can run complex, multi-dimensional aggregate queries across billions of rows, with response times far faster than querying the same data in S3 via Athena.

## 8.2 This Week's Deep Dive: Data Lake Engineering and Vector Search (Day 17–18)

**① Data lakes, Glue, and Athena (Day 17)**
- Data layering: **Raw (kept as-is) → Bronze (format standardized) → Silver (business-cleaned, analysis-ready) → Gold (aggregated and modeled, ready to use)** — data quality rises with each layer while data volume typically shrinks (driven by aggregation, not by cleaning).
- **Parquet's columnar storage** lets queries skip columns they don't need, and same-type data compresses better — faster and cheaper than row-based CSV.
- **Glue's three pieces**: Crawler (scouts and infers schema) → Data Catalog (stores metadata, not the actual data) → ETL Job (does the actual data processing, often followed by another Crawler run to update the catalog).
- **Athena bills by data scanned**: partitioning skips irrelevant folders, and columnar storage skips irrelevant columns — **these two savings multiply, they don't just add** — together they can shrink a bill to a tiny fraction of what it would otherwise be.
- **Five steps of RAG data cleaning**: ① ingestion → ② text extraction (format standardization) → ③ cleaning and deduplication → ④ sensitive-data handling (PII detection/masking) → ⑤ structuring and metadata tagging (department/date/permissions, enabling filtering and multi-tenant isolation).

**② Vector search and OpenSearch (Day 18)**
- **Embedding** turns text into a coordinate point — semantically similar text sits close together; **cosine similarity** (direction only, ignoring magnitude) is the most common metric for text retrieval.
- Exact matching is too slow at scale, so **approximate nearest neighbor (ANN)** trades some accuracy for speed; **HNSW** achieves fast, reasonably accurate results via a multi-layer "road network" (sparse upper layers for fast jumps, dense lower layers for fine-grained positioning).
- Semantic search has blind spots — **proper nouns, precise IDs, and specific numbers** don't lend themselves well to being semantically represented (they get "diluted" by neighboring years/IDs), so **BM25 keyword matching** is used to nail down exact text, combined with vector search in a **hybrid** approach that plays to each one's strengths.
- **OpenSearch Serverless has a minimum OCU billing floor** — you pay continuously for the minimum reserved OCUs even with zero traffic, which is why many companies opt for Aurora + pgvector as their vector store instead.

## 8.3 Architecture / Flow Diagrams (Described in Text)

**Five steps of RAG data cleaning**
```
① Ingestion (Raw layer) → ② Text extraction (format standardized, maps to the Bronze layer)
→ ③ Cleaning and deduplication (removing noise and duplicate content)
→ ④ Sensitive-data handling (PII detection/masking)
→ ⑤ Structuring and metadata tagging (department/date/permission labels, enabling downstream filtering and multi-tenant isolation)
```

**The two stacked layers of Athena cost optimization**
```
Unpartitioned CSV, querying one day's data → full scan, scanned data = entire dataset
Parquet partitioned by day, querying one day's data → partitioning first skips the other 364 days (leaving 1/365th of the data)
→ then columnar storage skips unneeded columns (further compression) → the two effects multiply, they don't just add
```

---

# Module 9: Management & Governance (8 services)

## 9.1 Overview of All 8 Services

### ★★★ Amazon CloudWatch
**The monitoring five-piece set: Logs / Metrics / Alarms / Logs Insights / Dashboard**

*(Covered in depth this week on Day 19 — see section 9.2 below; omitted here.)*

### ★★☆ AWS X-Ray
**Distributed request tracing**

*(Covered in depth this week on Day 19 — see section 9.2 below; omitted here.)*

### ★★☆ AWS CloudTrail
**A record of who called which AWS API**

*(Covered in depth this week on Day 19 — see section 9.2 below; omitted here.)*

### ★★☆ AWS Systems Manager
**A unified platform for ops actions and configuration management**

Systems Manager is a collection of ops tools, with its core capabilities being Parameter Store (centralized configuration parameters), Session Manager (logging into EC2 for ops work with no keys and no bastion host), and Patch Manager (automated bulk patching) — consolidating a lot of scattered ops tasks into one place.

**Example**: A team needs to log into an EC2 instance in a private subnet to troubleshoot. Previously this meant standing up a bastion host; now they use Session Manager directly — no inbound ports opened, no SSH keys to manage, just a click in the browser to get in.

### ★★☆ AWS CloudFormation
**AWS's native declarative infrastructure configuration**

*(Covered in depth this week on Day 20 — see section 10.2 below; omitted here — note that although it was taught alongside CDK/Terraform this week, it actually belongs to the "Management & Governance" module, not "Developer Tools.")*

### ★★☆ AWS Well-Architected Tool
**A self-assessment tool for architecture review**

The Well-Architected Tool walks you through a systematic self-review of your architecture against AWS's official six pillars (operational excellence, security, reliability, performance efficiency, cost optimization, sustainability). After answering a set of questions, it generates a report identifying where you've deviated from best practices, with concrete recommendations.

**Example**: An FDE doing an architecture review for a client imports the client's architecture into the Well-Architected Tool and systematically works through the checklist for all six pillars, producing a well-substantiated recommendations report instead of relying on ad hoc personal judgment.

### ★★☆ Cost Explorer / Budgets / Cost Anomaly Detection
**A cost-visibility, budget-alerting, and anomaly-detection trio**

Cost Explorer visualizes historical spend and breaks it down by service, tag, or account; Budgets lets you set spending caps that automatically trigger alerts when exceeded; Cost Anomaly Detection uses machine learning to automatically flag things like "spending suddenly spiked this month" without you having to manually scan billing tables for anomalies.

**Example**: A team reviews last month's spending breakdown by project with Cost Explorer at the start of each month, while also setting monthly Budget alerts per project. One day, Cost Anomaly Detection flags a sudden spending spike (a test environment someone forgot to shut down), and the team gets notified right away to investigate.

### ☆☆☆ Service Catalog / Control Tower / Trusted Advisor
**A multi-account governance trio**

Service Catalog lets an organization publish pre-approved, standardized resource templates for teams to self-serve, avoiding a mess of ad hoc, non-compliant configurations; Control Tower helps you quickly stand up and govern a multi-account AWS environment following best practices (automatically applying guardrail rules); Trusted Advisor automatically scans your account and offers recommendations on cost, security, performance, and fault tolerance.

**Example**: A large enterprise uses Control Tower to establish guardrail rules across a multi-account environment. Teams can only provision new resources from pre-approved templates in Service Catalog, while periodically reviewing Trusted Advisor's recommendations to optimize idle resources.

## 9.2 This Week's Deep Dive: The Observability Trio (Day 19)

- **CloudTrail**: records "who did what to AWS resources" (control-plane auditing) — indifferent to business logic.
- **CloudWatch Logs**: records "what the program itself printed" (application-level business logs) — indifferent to whether an AWS API was called.
- **X-Ray**: stitches together every service a single request passed through into one complete chain — a **Trace** (the whole journey) contains **Segments** (each stop along the way), which contain **subsegments** (finer-grained actions within a given stop).
- **CloudWatch's five-piece breakdown**: Logs (raw text), Metrics (numeric time-series data — a category/container, not a specific metric itself), Alarms (watches a Metric and fires when a threshold is crossed), Logs Insights (interactive log search), Dashboard (assembles everything into a visual view).
- **LLM-specific metrics**: TTFT (time to first token — measures whether it "feels like it started responding right away"), token usage, cost attribution, refusal rate, error/retry rate.
- **Bedrock's Model Invocation Logging** is off by default; it records the full prompt sent, the full response returned, which model was used, and token usage for every call — the primary source of data for troubleshooting and compliance auditing.

## 9.3 Architecture / Flow Diagrams (Described in Text)

**The decision criteria for the three observability tools**
```
Who touched an AWS resource (operational audit) → CloudTrail
What did the program itself say (business logs) → CloudWatch Logs
Which steps did a request pass through, and how long did each take (distributed tracing) → X-Ray
```

---

# Module 10: Developer Tools (7 services)

## 10.1 Overview of All 7 Services

### ★★★ AWS CDK
**Write infrastructure in a programming language; it compiles to CloudFormation**

*(Covered in depth this week on Day 20 — see section 10.2 below; omitted here.)*

### ★★★ Terraform (not an AWS product, but extremely widely used in enterprises)
**A cross-cloud declarative IaC tool**

*(Covered in depth this week on Day 20 — see section 10.2 below; omitted here.)*

### ★★☆ Kiro
**AWS's agentic IDE**

Kiro is AWS's next-generation development tool, launched in 2025, positioned as an "agentic IDE" — rather than just autocompleting code like a traditional AI coding assistant, it understands a much broader project context and can autonomously break down and execute multi-step development tasks (everything involved in "implement this feature" — creating files, writing code, writing tests, running tests).

**Example**: A developer asks Kiro to "implement a user registration endpoint, including input validation and unit tests." Kiro can autonomously plan out which files need changes, what code to write, and generate the corresponding tests — not just autocomplete the line currently being typed.

### ★★☆ Amazon Q Developer
**An AI coding assistant**

Amazon Q Developer is AWS's AI programming assistant, integrated into mainstream IDEs, offering code autocompletion, code explanation, generating code from natural-language descriptions, and automated code review plus security vulnerability scanning. It's positioned more as an "assistant for the writing and review stages of coding," distinct from Kiro's positioning as something that autonomously executes an entire development task.

**Example**: A developer with the Q Developer plugin installed in VS Code gets real-time autocomplete suggestions while typing, and before committing code, it automatically scans for potential security vulnerabilities and non-compliant patterns.

### ★★☆ CodePipeline / CodeBuild / CodeDeploy
**AWS's native CI/CD trio**

These three services each handle a different stage of the CI/CD process — CodePipeline orchestrates the entire pipeline (triggering build, test, and deploy stages in sequence after a code push); CodeBuild compiles code, runs tests, and packages it; CodeDeploy actually deploys the built artifact to EC2, Lambda, or ECS. Together they form a complete pipeline from code commit to automatic release, though in practice many teams still prefer third-party tools like GitHub Actions.

**Example**: A team sets up a pipeline where, after a developer pushes code to the repository, CodePipeline automatically triggers CodeBuild to compile and run unit tests; once tests pass, CodeDeploy automatically deploys the new version to production — no manual intervention required.

### ★★☆ AWS Amplify
**A full-stack rapid development platform**

Amplify lets you quickly assemble a complete full-stack application — frontend hosting, backend APIs, authentication (integrated with Cognito), and a database — with a large set of ready-to-use components and CLI tooling. Particularly well suited to fast PoCs, demos, or small-to-medium projects, without manually wiring together each AWS service by hand.

**Example**: An FDE needs to quickly build a demo application for a client. With a few Amplify commands, they stand up a working skeleton with frontend hosting, Cognito login, and a backend API — ready to demo within hours, instead of days of manual assembly.

### ☆☆☆ AWS CodeArtifact / AWS Cloud9
**Package management and a cloud IDE (lower priority, can be skipped)**

CodeArtifact is a managed package/dependency repository service (like a private version of npm/PyPI); Cloud9 is a browser-based cloud IDE. Neither comes up often in the day-to-day work of an AI Engineer/FDE — fine to skip in Phase 1 and just note that they exist.

## 10.2 This Week's Deep Dive: Choosing Among Three IaC Tools (Day 20)

- **Declarative (describes the target state) vs. imperative (describes the operational steps)**: declarative tools automatically diff the current state against the target state and only execute the difference, giving them **idempotency** — safe to run repeatedly. An imperative script rerun is prone to erroring out on "already exists" or duplicating resources.
- **CloudFormation**: a Stack manages the full lifecycle of a set of resources as one unit; a **change set** previews exactly what will be added/changed/deleted before you actually execute an update; **drift detection** catches manual changes made outside of IaC.
- **CDK**: write infrastructure in TypeScript/Python, but it **still compiles down to a CloudFormation template** — it isn't an independent engine. L1 (close to the metal, everything must be configured), L2 (sensible defaults, the most commonly used day-to-day), L3 (an entire architecture pattern bundled up — convenient but least customizable).
- **Terraform**: cross-cloud capability comes from **Provider** plugins; a **State file** records "what the real world currently looks like" — in team settings this must be **stored remotely and shared**, or multiple people operating from stale local state will conflict and overwrite each other; **Modules** provide reusability.
- **CDK vs. Terraform is not either/or**: pure-AWS teams with developers comfortable writing code → CDK; multi-cloud environments or teams with existing Terraform experience → Terraform. Both can coexist within the same organization, each handling a different slice.

## 10.3 Architecture / Flow Diagrams (Described in Text)

**IaC tool selection decision path**
```
Need multi-cloud support (AWS + Azure, etc.) or the team already has Terraform experience → Terraform
Pure AWS environment + developers comfortable writing in a programming language → CDK
Just need native YAML/JSON with no need for programming-language reusability → CloudFormation directly
```
