# Module 3: Compute (9 services)

## 3.1 Overview of All 9 Services

### ★★★ Amazon EC2
**Virtual servers in the cloud**

EC2 is Amazon's elastic compute service, letting users rent virtual servers (called instances) to run all kinds of applications. Instances can scale up or down flexibly based on demand, and users can choose from different instance types (compute-optimized, storage-optimized, memory-optimized, etc.) to match the performance needs of different applications. You can deploy any operating system and application on an instance, with full control over its configuration and management, and you pay based on the resources and time you actually use. EC2 is one of the core pieces of infrastructure for building and hosting virtually any cloud workload.

**Example**: A startup hosts its website on EC2 — some instances run the front end, others run the database — and can flexibly adjust the number of instances as site traffic changes. The same elastic compute is also used to spin up a temporary data-processing cluster; once the market research data has been analyzed, the instances are shut down to avoid unnecessary cost.

### ★★★ AWS Auto Scaling
**Automatically adds or removes capacity**

Auto Scaling automatically increases or decreases the number of EC2 instances (or other scalable resources) based on policies you define — for example, add instances when CPU usage exceeds 70%, remove them when it drops below 30% — keeping your application supplied with just the right amount of capacity at all times. It doesn't buckle under a sudden traffic spike, and it doesn't waste money on idle resources during a lull. It supports three scaling approaches: target tracking (automatically adjusting to hold a metric at a target value), step scaling (adjusting in tiers based on thresholds), and scheduled scaling (pre-planning capacity changes for specific times).

**Example**: An e-commerce site configures target tracking on CPU utilization. During a big sale, traffic surges and dozens of extra instances spin up automatically to absorb the load; once the sale ends and traffic drops, the extra instances are automatically shut down.

### ★★☆ AWS Batch
**Scheduling for large-scale batch processing jobs**

Batch automatically manages the compute resources needed to run batch-processing jobs — you simply submit a job (e.g., "process these 1,000 files"), and it automatically decides how many machines of what type to use to run it, releasing the resources once the job finishes. You never have to manually manage the lifecycle of that compute yourself.

**Example**: A medical imaging company needs to analyze tens of thousands of scans every day. They submit the job to Batch, which automatically provisions enough compute to process them in parallel and releases it once processing is complete.

### ★★★ AWS Elastic Beanstalk
**A platform-as-a-service deployment layer**

Elastic Beanstalk lets you simply upload your application code, and it automatically handles deploying the underlying infrastructure — EC2 instances, load balancing, Auto Scaling, monitoring — all configured for you without manual setup, while still letting you view and fine-tune the underlying resources, unlike a more "black box" serverless approach where you can't see underneath at all.

**Example**: A small team wants to launch a web app quickly without manually configuring load balancers and other infrastructure from scratch. They upload their code package to Elastic Beanstalk and have a fully scalable deployment running within minutes.

### ★★★ Amazon Lightsail
**Simplified cloud hosting for getting started and small projects**

Lightsail offers pre-packaged virtual server plans with fixed pricing and simple configuration (bundling compute, storage, and network transfer), particularly well suited to scenarios that don't require deep cloud architecture knowledge — personal blogs, small business websites, dev/test environments. It sits somewhere between "traditional shared hosting" and "full EC2": easier to configure and easier to predict costs for, but less flexible and less scalable than using EC2 directly.

**Example**: A freelancer wants to build a personal portfolio site without needing complex cloud architecture. They pick a fixed monthly Lightsail plan and have a configured server ready to deploy to within minutes.

### ★★★ AWS Lambda
**Serverless function compute**

*(Covered in depth this week on Day 8–9 — see section 3.2 below; omitted here.)*

### ☆☆☆ AWS Outposts
**Extends AWS infrastructure into your own data center**

Outposts physically deploys AWS hardware and software into a customer's own data center, letting them use the same APIs and tools on-premises as they would in the AWS cloud, while satisfying requirements that data stay physically local.

**Example**: A bank is required by regulation to keep core data from ever leaving its own data center, but still wants the AWS development experience. They deploy Outposts hardware in their own facility, processing data locally while keeping a consistent operational experience with the cloud.

### ☆☆☆ AWS Wavelength
**Brings compute to the 5G network edge**

Wavelength deploys AWS compute and storage resources at the edge of telecom carriers' 5G networks, so end-user requests don't have to travel all the way to a distant AWS Region and can instead be handled right at the network edge near the user — ideal for applications that are extremely latency-sensitive.

**Example**: An AR/VR application that requires ultra-low latency deploys its critical compute on the nearest 5G Wavelength edge node, significantly cutting end-to-end response latency.

### ☆☆☆ AWS Local Zones
**Extends an AWS Region closer to your city**

Local Zones are extension sites of an AWS Region deployed near major metropolitan areas, giving latency-sensitive applications that don't want to be tied to Wavelength's carrier-specific 5G model a compute node that's still closer to their users.

**Example**: A video post-production company needs extremely low latency for processing large render files. They use the Local Zone nearest their office instead of the main Region, cutting network transfer latency.

## 3.2 This Week's Deep Dive: Lambda and Compute Selection (Day 8–9)

**① Lambda deep dive (Day 8)**
- A cold start is the total time for re-creating the execution environment, starting the runtime, and running any initialization code outside the handler. Memory/CPU allocation, package size, language runtime, and whether the function is VPC-attached all affect cold-start duration.
- **Provisioned concurrency**: paying to keep execution environments pre-warmed, skipping the cold start. **Reserved concurrency**: carving out a dedicated concurrency quota for a function that other functions can't consume. These handle two completely different problems and can be configured independently or together.
- Concurrency draws from a **shared pool across the entire account** by default (1,000 by default) — a traffic spike in one function can consume another function's quota and get it throttled.
- **The 15-minute hard limit**: tasks that can be broken into steps get relayed through Step Functions; tasks that can't (because they need a long connection or complex in-memory state) move to Fargate instead.
- **Response streaming**: makes the user feel like the response starts "immediately," rather than staring at a blank screen. Currently only available via a **Function URL** — API Gateway doesn't support streaming forwarding.
- **Layers** (250MB total size cap, good for lightweight shared dependencies) vs. **container image deployment** (10GB cap, good for heavy dependencies or an existing Docker image).

**② Compute selection (Day 9)**
- The selection spectrum: event-driven/tolerates cold starts/bounded single execution → Lambda; long-running/long connections/no strict duration limit (especially agent frameworks) → Fargate; fast containerized web service deployment with no interest in orchestration → App Runner (not among the 9 services in the Compute module screenshot — a confirmed gap); needs OS-level control or a GPU → EC2.
- **GPU instances**: the G-family is for "inference" (the model is already trained; use it to answer questions), the P-family is for "training" (training from scratch or heavy fine-tuning). Calling a managed model service like Bedrock means you never have to think about GPUs at all — only self-hosted models require picking one yourself.
- **Graviton (ARM architecture)**: typically about 20% cheaper than the equivalent x86 instance at the same spec, but not every piece of software or container image natively supports ARM — confirm your whole stack is compatible before switching.

## 3.3 Architecture / Flow Diagrams (Described in Text)

**Three angles for troubleshooting "the AI app is always slow the first time"**
```
① Check the REPORT line in CloudWatch Logs for an Init Duration field → present means it's a genuine Lambda cold start
② If the function is VPC-attached, compare Init Duration against a similar non-VPC function → a clear gap points to ENI setup overhead
③ If Init Duration is short but total Duration is still long → the problem is downstream (database/Bedrock/etc.), not Lambda itself
```

**Compute selection decision path**
```
Event-driven, tolerates cold starts, bounded single execution → Lambda
Needs to stay running, long connections, no strict duration limit (especially agent frameworks) → Fargate
Just wants a containerized web service deployed fast, no interest in orchestration → App Runner
Needs OS-level control, or a GPU (G-family for inference / P-family for training) → EC2
```

---

# Module 4: Containers (4 services)

## 4.1 Overview of All 4 Services

### ★★★ Amazon ECS (Elastic Container Service)
**AWS's native container orchestration service**

ECS manages and schedules a fleet of Docker containers, deciding which resources they run on and handling health checks and automatic restarts. It's an orchestration system AWS designed itself, integrating very smoothly with other AWS services (ALB, CloudWatch, Fargate), with a gentler configuration and learning curve than Kubernetes.

**Example**: A team splits its application into several microservice containers and uses ECS to centrally orchestrate their deployment, scaling, and health checks, instead of managing each one by hand.

### ★★★ Amazon EKS (Elastic Kubernetes Service)
**Managed Kubernetes**

EKS is AWS's managed Kubernetes service, built on the industry-standard orchestration technology used across cloud providers. Compared to ECS, EKS is more complex to configure, but in exchange offers stronger portability and a richer open-source ecosystem — well suited to teams that already have Kubernetes experience, or that need multi-cloud deployment to avoid vendor lock-in.

**Example**: A company that already manages its containers with Kubernetes on another cloud provider migrates to AWS and chooses EKS over ECS, since the team's existing Kubernetes configuration and tooling can carry over almost unchanged.

### ★★★ Amazon ECR (Elastic Container Registry)
**A managed container image registry**

ECR is a managed registry for storing Docker container images, integrating seamlessly with ECS, EKS, and Lambda, and supporting image versioning and vulnerability scanning. You build an image, push it to ECR, and pull it from there at deploy time — no need to build and maintain your own registry.

**Example**: A team's CI/CD pipeline automatically builds a new container image and pushes it to ECR on every code commit; at deploy time, ECS pulls the latest image directly from ECR.

### ★★★ AWS Fargate
**Serverless container runtime**

*(Covered in depth this week on Day 9 — see section 4.2 below; omitted here.)*

## 4.2 This Week's Deep Dive: Fargate and ECS/EKS Selection (Day 9)

- Fargate is "serverless but long-running" — you don't manage the underlying EC2 hosts, but it runs a container that stays up continuously. There's no 15-minute wall, and it can maintain long connections. The trade-off is it's not zero-cost-when-idle like Lambda — it's billed continuously while running.
- Fargate is the default runtime for agent frameworks: the combination of long connections, heavy dependencies, and the need to maintain in-memory state naturally fits a long-running container, not a "run once per request" Lambda.
- The ECS-vs-EKS decision comes down to **whether you need multi-cloud and whether the team already has Kubernetes experience** — not which one is "better." Absent those two reasons, ECS is usually the more low-maintenance choice.

## 4.3 A Note

All 4 items in the Container module screenshot are rated ★★★, indicating the course covers this area fairly thoroughly at the CCP level. This week only touched it through a selection comparison, without going deeper into ECS/EKS operational details — a reasonable call, since there's no need for Phase 1 to re-dig into ground the course has already covered well.

---

# Module 5: Storage (7 services)

## 5.1 Overview of All 7 Services

### ★★★ Amazon EBS (Elastic Block Store)
**Block storage attached to EC2**

EBS provides persistent block storage volumes for EC2 instances — like attaching a hard drive to a virtual machine — with data surviving instance stops and restarts. It supports different performance tiers (general-purpose SSD, high-performance IOPS-optimized), suited to workloads needing low-latency, high-throughput random reads and writes, such as a database's storage layer.

**Example**: An EC2 instance running MySQL stores its data files on a high-performance EBS volume. Even if the instance restarts, the data remains fully intact on that volume.

### ★★★ Amazon EFS (Elastic File System)
**Elastic file storage that multiple machines can mount at once**

EFS provides a shared file system over the NFS protocol that scales capacity automatically. Its standout feature is that **multiple EC2 instances (even Lambda) can mount and read/write it simultaneously**, something EBS can't do (an EBS volume is typically attached to only one instance at a time). Well suited to scenarios where multiple machines need to share the same set of files.

**Example**: A video-processing cluster with multiple EC2 instances all needs to read the same batch of source files. They mount EFS across every instance, sharing one storage pool instead of each keeping its own copy.

### ★★☆ Amazon FSx
**Managed third-party file systems**

FSx provides managed versions of several popular third-party file systems (Windows File Server, the Lustre high-performance-computing file system, NetApp ONTAP, etc.), suited to workloads that already depend on one of these specific file system technologies and don't want to re-architect their application when moving to the cloud.

**Example**: A company's Windows application has long depended on Windows File Server for file sharing. When they move to the cloud, they use FSx for Windows File Server, and the application code doesn't need any changes to use the managed cloud version.

### ★★★ Amazon S3
**Object storage**

*(Covered in depth this week on Day 11 — see section 5.2 below; omitted here.)*

### ★★★ Amazon S3 Glacier
**Ultra-low-cost archival storage**

Glacier is an S3 storage class purpose-built for data that's rarely accessed but must be retained long-term, priced far below standard S3. The trade-off is that retrieving the data takes extra time (from minutes to hours, depending on the retrieval speed tier chosen) and incurs a retrieval fee. Commonly used for compliance-driven long-term data retention.

**Example**: A healthcare organization is required by regulation to retain medical records for 7+ years, even though those records are almost never accessed. They store them in Glacier Deep Archive, keeping storage cost to a minimum while meeting the retention requirement.

### ★★☆ AWS Storage Gateway
**A hybrid-cloud gateway bridging on-premises and cloud storage**

Storage Gateway lets on-premises applications access AWS cloud storage as if it were local storage. Under the hood, it's a gateway device deployed on-premises that translates requests into calls to S3 (or other cloud storage), while caching hot data locally to speed up access.

**Example**: A company wants to gradually migrate its on-premises file server to the cloud without abruptly disrupting local applications. Storage Gateway lets local applications keep accessing files the same way they always have, while the data is actually already being synced to S3 in the background.

### ★★☆ AWS Backup
**A unified backup management service**

Backup lets you centrally manage backup policies across multiple AWS resource types (EC2, EBS, RDS, DynamoDB, etc.) from one place — setting backup frequency, retention duration, and cross-region replication rules and pushing them out uniformly, instead of configuring a separate backup mechanism for each resource type.

**Example**: A company used to configure separate backup scripts for EC2 and RDS independently, which became hard to manage. After switching to AWS Backup, they set backup schedules and retention policies for every resource from a single console.

## 5.2 This Week's Deep Dive: S3 Core Mechanics (Day 11)

- **Four notification destinations**: a single processing action goes to Lambda; buffering against spikes goes to SQS; broadcasting one event to multiple independent recipients goes to SNS; complex filtering/routing goes to EventBridge.
- **Presigned URLs**: the backend generates a signed, time-limited, permission-scoped temporary link that the frontend uses to talk directly to S3, bypassing the backend server for the file itself — but a presigned URL by itself **has no built-in "notify someone once uploaded" capability**; that requires a separately configured event notification to complete the flow.
- **The four encryption options**: SSE-S3 (fully managed, free), SSE-KMS (auditable, the option most often required by enterprise compliance questionnaires), SSE-C (customer manages the key themselves), DSSE-KMS (double encryption, for the strictest compliance scenarios).
- **Versioning + lifecycle rules**: deletion just adds a delete marker — historical versions remain. Lifecycle rules handle automatically moving old versions to colder storage or purging them entirely to control cost.
- **Strong consistency**: since December 2020, every S3 operation (create, overwrite, delete) has been strongly consistent — writing and then immediately reading is guaranteed to return the latest content, so there's no longer any need for defensive retry logic to handle stale reads.

## 5.3 Architecture / Flow Diagrams (Described in Text)

**User uploads a PDF → processing is triggered automatically**
```
Frontend requests a presigned URL from the backend → frontend PUTs the file directly to S3 (bypassing the backend server)
→ a separately configured S3 event notification (e.g., triggering Lambda) → Lambda wakes up and processes the PDF (e.g., calls Textract)
→ results are stored back in S3 or written to a database → frontend either polls for status or is notified through a separate mechanism
```

---

# Module 6: Databases (5 services)

## 6.1 Overview of All 5 Services

### ★★★ Amazon RDS (Relational Database Service)
**A managed relational database**

*(Covered in depth this week on Day 12 — see section 6.2 below; omitted here.)*

### ★★★ Amazon Aurora
**AWS's high-performance, cloud-native relational database**

*(Covered in depth this week on Day 12 — see section 6.2 below; omitted here.)*

### ★★★ Amazon DynamoDB
**A fully managed NoSQL database**

*(Covered in depth this week on Day 13 — see section 6.2 below; omitted here.)*

### ★★★ Amazon MemoryDB for Redis
**A Redis-compatible, durable in-memory database**

*(Covered in depth this week on Day 13 — see section 6.2 below; omitted here.)*

### ☆☆☆ Amazon Neptune
**A managed graph database**

Neptune is purpose-built for storing and querying graph-structured data made up of nodes and relationships — like "who knows whom" in a social network, or "who depends on whom" in a supply chain. It supports graph query languages like Gremlin and SPARQL, and is well suited to scenarios with complex relationships and multi-hop queries, where a traditional relational database's performance degrades sharply. Its variant, Neptune Analytics, also adds vector capability, useful for GraphRAG scenarios.

**Example**: An e-commerce platform wants to power "people who bought this also bought..." and "these people also follow which other products" style multi-hop recommendations. They store the user-product relationship graph in Neptune, where multi-hop queries run far more efficiently than doing repeated JOINs in a relational database.

## 6.2 This Week's Deep Dive: Relational Databases, Vector Storage, and DynamoDB/Caching (Day 12–13)

**① Relational databases and vector storage (Day 12)**
- **Multi-AZ vs. Read Replica**: the Multi-AZ standby is a "spare tire" — not readable day-to-day, only takes over on primary failure, and exists for high availability. A Read Replica is "another car you can drive" — readable, dedicated to offloading read traffic, and exists for read scaling.
- **Aurora's storage/compute separation**: the storage layer automatically maintains 6 copies across 3 Availability Zones, delivering faster crash recovery (seconds) and faster replica creation.
- **Aurora Serverless v2**: scales in **0.5 ACU** steps within seconds without dropping connections, and can be configured to pause automatically at a minimum of **0 ACU** (with roughly a 15-second wake-up delay).
- **pgvector**: not a standalone product — it's a PostgreSQL extension that rides on an Aurora bill and operational experience you already have, making it the cheapest option for a RAG vector store.
- **IVFFlat vs. HNSW**: IVFFlat builds faster and uses less memory, but accuracy is sensitive to how many clusters you choose. HNSW queries faster and is generally more accurate, but takes longer to build and uses more memory. Production-grade scenarios usually default to HNSW.

**② DynamoDB and caching (Day 13)**
- **Partition keys and hot partitions**: the partition key determines how data is spread out; a field with too few distinct values, with requests concentrated on just a handful of them, causes a "hot partition" (a few partitions get overloaded while the rest sit idle).
- **Single-table design**: since DynamoDB doesn't support JOINs, data types that are frequently queried together are packed into the same table using a deliberate key structure, so one request can retrieve everything needed.
- **Streams**: a change-data-capture mechanism for data modifications, following the same idea as S3 event notifications, commonly used to trigger Lambda for downstream actions (handles "did something change that should automatically trigger an action").
- **TTL**: attach an expiration timestamp to a record so it cleans itself up automatically (not instantly — expiry kicks off a deletion process with some delay).
- **ElastiCache (Redis) vs. MemoryDB for Redis**: the former is a pure cache where "losing it is fine" — good for semantic caching. The latter is durable primary storage where "losing it isn't an option" — good for agent session state.

## 6.3 Architecture / Flow Diagrams (Described in Text)

**Inventory change → automatically triggers a low-stock check (DynamoDB Streams)**
```
An inventory quantity field is modified → DynamoDB Streams captures the change
→ triggers Lambda → Lambda runs the low-stock check logic (e.g., alerts if below a threshold)
```

**Deciding where to store agent session state**
```
Ask yourself: "If this data is lost, does it just get slower, or does something actually break?"
→ Losing it just means slower (e.g., semantic cache — re-call the model) → ElastiCache
→ Losing it breaks something (e.g., a conversation drops mid-flow, task context disappears) → MemoryDB for Redis
```

---

# Supplement: Networking Services Touched on Day 10

Day 10 (traffic entry points and LLM streaming) covers API Gateway, which was already given a full write-up in the "Networking & Content Delivery" module in the Week 1 notes — it isn't repeated here. This section only adds what was newly covered this week, plus two services whose course coverage status needs a note.

**API Gateway's 29-second timeout**
- REST API is full-featured but pricier; HTTP API is cheap and fast but leaner. Both are subject to a **hard 29-second timeout**.
- Three ways around it: ① use streaming (a streaming connection isn't judged as "stuck"); ② switch to an async pattern (return a task ID immediately, then poll or push a notification later); ③ move to an entry point that isn't subject to this limit (see ALB below).

**AWS ALB (Application Load Balancer)** — ⚠️ course coverage unconfirmed due to an incomplete screenshot
- ALB doesn't appear in the Networking module screenshot, but the bottom-right corner of the Compute module screenshot is cut off, so it's possible there are items not captured that weren't included here. Whether the course covers ALB can't currently be confirmed with certainty.
- On the substance: ALB is fundamentally a load balancer, not a managed gateway. Its default idle timeout is 60 seconds, tunable up to 4000 seconds, making it very friendly to long responses and streaming. It can target both Lambda and containers, just as API Gateway can — **the real dividing line for choosing between them is whether you need long responses/streaming, not the backend type.**

**AWS AppSync** — confirmed via screenshot as not covered by the course (absent from the Networking module's 8 services)
- Built on GraphQL's Subscription mechanism: the frontend subscribes to a "channel," and the backend calls a Mutation to push new content each time it finishes a small chunk of processing, with AppSync automatically broadcasting it to every subscriber.
- The effect resembles a typewriter animation, but it travels over GraphQL subscriptions — essentially a layer wrapped around WebSocket.

**Three ways to implement streaming**
- **Polling**: the simplest option but with noticeable perceived latency — a reasonable fallback when the experience doesn't need to be polished.
- **SSE (Server-Sent Events)**: one-way, server-initiated continuous push, natively supported by browsers. On AWS this is typically implemented via **Lambda Function URL + response streaming**, and is currently the most common way to implement the LLM typewriter effect.
- **WebSocket**: full-duplex, implemented via **API Gateway's WebSocket API**, suited to scenarios where the user needs to interrupt the model mid-generation — a two-way interaction.
