# AWS Generative AI — Study Notes & Review Console

*Status: actively maintained — the `practice/` folder in particular keeps growing as I complete more labs.*

Personal study repository built while working toward the **AWS Certified Generative AI Developer – Professional (AIP-C01)** exam.

It picks up after an entry-level AWS Cloud Practitioner overview course and works through a structured, 4-week "concept-completion" pass — filling in the networking, security, compute, data and (mainly) generative-AI depth that a beginner-level course doesn't cover — then moves into hands-on AWS Console labs (`practice/`) on the way to full exam prep.

If you're an interviewer skimming this: it's evidence of a self-directed learning process, not a finished credential — the notes are working documents, written to be *understandable*, not polished marketing copy. If you're a fellow learner: feel free to reuse the structure, the review console, or the lab write-ups for your own AIP-C01 prep.

This is an independent personal project — not affiliated with, endorsed by, or reviewed by AWS.

## What's inside

```
AWS/
├── README.md                # this file
├── AWS_AIP-C01.html         # interactive, offline review console — open directly in a browser
├── graph/                   # bilingual reference diagrams (knowledge map + quick-reference cards)
├── week-1/ … week-4/        # module-by-module study notes (中文 / English)
└── practice/                # hands-on AWS Console lab write-ups, bilingual — growing over time
```

## The review console — `AWS_AIP-C01.html`

A single self-contained HTML file with no build step and no server — just open it in a browser. It compiles four weeks of notes into one interactive study tool:

- **14 knowledge modules, 115 services and concepts** — networking, security/IAM, compute, containers, storage, databases, application integration, analytics, management & governance, developer tools/IaC, plus a dedicated generative-AI track (Bedrock's Converse API, model selection & pricing, Tool Use, Knowledge Bases/RAG, Guardrails, AgentCore, and the non-product methodology behind RAG, prompt, and Agent engineering)
- **14 decision trees** for "which service do I actually pick" questions (compute, messaging, vector store, IaC tool, RAG chunking strategy, and more)
- **13 side-by-side comparison cards** for the pairs everyone mixes up (Security Group vs NACL, Retrieve vs RetrieveAndGenerate, Knowledge Bases vs Kendra vs Amazon Q Business, …)
- **41 architecture / flow diagrams**, rendered as inline SVG — request paths, decision flows, and structural breakdowns
- A **"panorama" view** stringing services into 6 real end-to-end scenarios: a synchronous RAG answer, streaming chat, a document-ingestion pipeline, a production Agent, offline batch processing, and the evaluation-and-iteration feedback loop that runs after launch
- A **32-question self-test quiz**, each answer explained
- One-click **中文 / English** toggle throughout

**Live demo:** also hosted as a static page on Amazon S3, so it's viewable without cloning the repo — **[AWS_AIP-C01.html on S3](https://aws-server-image-0820.s3.eu-west-1.amazonaws.com/AWS_AIP-C01.html)** (`eu-west-1`). Since it's public, I've set request-volume thresholds/alarms on the bucket as a guardrail against scraping or abusive traffic — treat the link as a personal demo rather than a guaranteed-uptime service, and expect it to occasionally lag behind the copy in this repo.

## Weekly notes

| Week | Focus |
|---|---|
| **Week 1** | Networking & content delivery (VPC internals, VPC Endpoints, PrivateLink) · Security, Identity & Compliance (IAM policy evaluation logic, roles & STS, Cognito) |
| **Week 2** | Compute (Lambda deep dive, Lambda vs Fargate vs EC2) · Containers · Storage (S3 mechanics) · Databases (RDS/Aurora, pgvector, DynamoDB, caching) |
| **Week 3** | Application integration (SQS/SNS/EventBridge, Step Functions) · Analytics (data lakes, Glue, Athena, vector search/OpenSearch) · Management & Governance (CloudWatch/X-Ray/CloudTrail, cost tools) · Developer tools & IaC (CDK/Terraform/CloudFormation) |
| **Week 4** | Generative AI on Bedrock — Converse API, model selection & the four pricing modes, Tool Use, Knowledge Bases & chunking, Guardrails, AgentCore — plus RAG engineering, prompt engineering, Agent engineering, evaluation & observability, and responsible AI |

## Hands-on labs — `practice/`

Step-by-step AWS Console walkthroughs, each written up bilingually. This folder is a living collection — new labs get added as I work through them. Currently covers:

1. VPC Peering
2. VPC Gateway Endpoint
3. CloudFront + S3 with Origin Access Control (OAC)
4. S3 public-access configuration
5. EFS mounted on EC2

## A note on accuracy

Some of the Week 3/4 service coverage and star ratings were estimated from a study-plan document rather than verified against course screenshots — this is called out inline wherever it applies, both in the markdown notes and inside the review console (look for the "estimated, unverified" tag). Treat this repo as a study log, not an authoritative reference: cross-check anything exam-critical against the official AWS documentation.
