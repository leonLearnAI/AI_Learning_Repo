# Module 1: Networking & Content Delivery (8 services)

## 1.1 Overview of All 8 Services

### ★★★ Amazon VPC
**A private network space in the cloud**

Amazon VPC (Virtual Private Cloud) lets you carve out a logically isolated private network inside AWS. You define your own IP address range (CIDR), create subnets, configure route tables and gateways, and decide which resources can reach the public internet and which stay fully isolated. VPC is the networking foundation underneath almost every AWS architecture — EC2, RDS, and Lambda (when VPC-connected) all run inside some subnet of some VPC, and you have full control over the entire network topology.

**Example**: A company places its website's front-end servers in a public subnet (reachable by users) and its database in a private subnet (not directly reachable from outside), using the VPC to separate the two layers — the site stays accessible while the database stays protected from public exposure.

### ★★★ Amazon API Gateway
**A managed entry point for APIs**

API Gateway is a fully managed service for creating, publishing, maintaining, monitoring, and securing REST, HTTP, and WebSocket APIs. You don't need to run your own servers to handle request routing, authorization, throttling, or monitoring — API Gateway takes care of all of it. It's frequently paired with Lambda to build a fully serverless backend: requests hit API Gateway first, which then triggers the corresponding Lambda function.

**Example**: A startup's mobile app has all of its backend logic implemented as Lambda functions. API Gateway exposes those functions as a standard REST API for the app to call, with no servers to maintain.

### ★★★ Amazon CloudFront
**AWS's global content delivery network (CDN)**

CloudFront caches your content (web pages, images, video, software packages, etc.) at edge locations distributed around the world. When a user makes a request, they're automatically routed to the nearest edge location, dramatically cutting latency. The origin can be S3, EC2, or even your own server, and CloudFront is often paired with WAF and ACM to form a complete accelerate + protect + HTTPS delivery stack for the front end.

**Example**: An e-commerce site stores its product images in S3 and puts CloudFront in front of it. Users around the world load images from the nearest edge location instead of crossing an ocean to hit the origin S3 bucket every time.

### ★★★ AWS Direct Connect
**A dedicated physical network connection to AWS**

Direct Connect establishes a dedicated physical network link between your data center and AWS that bypasses the public internet entirely, offering more consistent bandwidth and lower latency than a typical connection. Setup takes longer (physical cabling is involved, usually weeks to months) and costs more than a VPN, so it's mainly used by organizations moving large volumes of data with strict stability or compliance requirements.

**Example**: A multinational manufacturer needs to sync large volumes of factory sensor data to AWS every day for analysis. Their public-internet VPN kept getting congested, so they switched to Direct Connect and saw a major improvement in transfer stability and speed.

### ★★★ AWS Global Accelerator
**Routes global users to the nearest healthy endpoint**

Global Accelerator uses AWS's global backbone network — rather than the public internet — to route user requests to the nearest, healthiest application endpoint, while also providing fixed anchor IP addresses so the entry point stays the same even if the backend resources change. It's commonly used for latency-sensitive applications with a global user base that need automatic failover.

**Example**: A global online game uses Global Accelerator to route players on different continents to the nearest regional server, while keeping one consistent connection IP. If a region goes down, traffic automatically shifts to a healthy region and players barely notice.

### ★★★ Amazon Route 53
**A highly available DNS service**

Route 53 is AWS's DNS service, responsible for resolving domain names to IP addresses, and it also supports domain registration and health checks. Its standout feature is seven routing policies (simple, weighted, latency-based, failover, geolocation, geoproximity, and multi-value), which let you flexibly distribute traffic across resources based on where users are located or the health of your backends.

**Example**: A company runs one deployment in the US and another in Europe. Using geoproximity routing, US users automatically resolve to the US servers and European users to the European servers; with health checks configured, traffic automatically shifts to the other region if one goes down.

### ★★★ AWS VPN
**Encrypted connectivity to a VPC over the public internet**

AWS VPN builds an IPsec-encrypted tunnel between your on-premises network and a VPC. Traffic travels over the public internet, but it's fully encrypted in transit. Compared to Direct Connect, VPN is quick to set up (often configurable in minutes to hours) and cheaper, but its bandwidth and latency aren't as stable as a dedicated physical connection.

**Example**: A small-to-medium business wants remote employees to securely reach internal systems on AWS, without taking on the high cost and long lead time of Direct Connect, so they quickly stand up a Site-to-Site VPN for an encrypted tunnel.

### ★★★ AWS Transit Gateway
**A central hub for connecting many VPCs**

If an organization has dozens or even hundreds of VPCs that need to talk to each other, connecting them pairwise with VPC Peering creates a mesh that grows in complexity exponentially and becomes unmanageable. Transit Gateway provides a central hub that every VPC and on-premises network connects to just once, with the hub handling all the traffic forwarding — dramatically simplifying the management overhead of interconnected architectures.

**Example**: A large enterprise has dozens of VPCs for production, testing, and data analytics. Managing them with pairwise Peering had become chaotic; after switching to Transit Gateway, every VPC only needs a single connection to the hub, and adding a new VPC only requires one new connection instead of reworking a mesh of relationships.

## 1.2 This Week's Deep Dive: VPC (Day 1–3)

Of these 8 services, only **VPC** got a deep dive this week — but the deep dive actually covered four internal mechanisms within VPC: data-flow paths, Security Groups/NACLs, route-table path selection, and VPC Endpoints.

**① Determining public/private subnets and data flow (Day 1)**
- Whether a subnet is "public" or "private" comes down to **whether its route table has a 0.0.0.0/0 route to the IGW** — it's not an inherent property of the subnet. Remove that route and the subnet instantly becomes private.
- Public subnet outbound: the IGW performs **1:1 static NAT**, translating the private IP to the bound public/Elastic IP.
- Private subnet outbound: relies on a **NAT Gateway** doing **PAT (many-to-one) translation**. The NAT Gateway itself must sit in a public subnet, since it also needs that subnet's route to reach the internet.
- CIDR math: a /24 theoretically has 256 addresses; AWS reserves 5 (network address, router, DNS reservation, AWS-reserved, broadcast address), leaving 251 usable.

**② Security Groups, NACLs, and route-table path selection (Day 2)**
- Security Groups (instance level) are **stateful** — return traffic is automatically allowed, so you don't need to configure outbound rules.
- NACLs (subnet level) are **stateless** — inbound and outbound traffic each need their own rules, which is the most common source of one-way-broken connections from a missed rule.
- Security Groups **only support allow rules** — there's no way to deny a specific IP there. To blacklist an IP you have to add a **lower-numbered** deny rule at the NACL level (NACLs evaluate rules in ascending order and the first match wins).
- Route tables select a path using **longest prefix match** — the more specific match (the smaller range) wins, regardless of the order the rules are physically written in.

**③ VPC Endpoints and PrivateLink (Day 3)**
- By default, even calls to AWS's own services like S3 or Bedrock go out over the public internet (since they expose public endpoints), routing through the NAT Gateway and IGW.
- **Gateway type**: only serves S3 and DynamoDB, essentially just one more route table entry, uses no physical resources, and is **free**.
- **Interface type (PrivateLink)**: supports most services including Bedrock, and creates a **real network interface (ENI)** inside your subnet, billed hourly plus per-GB.
- PrivateLink exposes exactly one specific service (the other party can't see anything else in your VPC); VPC Peering fully connects the entire address space of two VPCs — the two serve different purposes.

## 1.3 Architecture / Flow Diagrams (Described in Text)

**Public subnet outbound**
```
EC2 (public/Elastic IP) → subnet route table (0.0.0.0/0 → IGW) → IGW (1:1 NAT) → internet
```

**Private subnet outbound**
```
EC2 (private IP only) → private subnet route table (0.0.0.0/0 → NAT Gateway)
→ NAT Gateway (PAT translation, lives in a public subnet) → public subnet's route table → IGW → internet
```

**An inbound request reaching an EC2 instance**
```
External request → IGW (1:1 NAT) → route table (decides which subnet)
→ NACL (subnet level, stateless) → Security Group (instance level, stateful) → EC2's network interface
```

**A private-subnet Lambda calling Bedrock without ever touching the public internet**
```
Lambda (in a private subnet) → private subnet route table → Bedrock's Interface Endpoint (private IP)
→ straight to Bedrock over AWS's internal network (no NAT Gateway, no IGW)
```

---

# Module 2: Security, Identity & Compliance (19 services)

## 2.1 Overview of All 19 Services

### ★☆☆ AWS Artifact
**A self-service portal for downloading compliance documents**

Artifact is a self-service, on-demand portal containing AWS's compliance reports and agreements — SOC 1/2/3 reports, PCI DSS certification documents, and various international/industry compliance certifications. When a company is undergoing a security audit or needs to prove to a customer that "the AWS infrastructure itself is compliant," they can download the official documents here directly, with no extra request needed.

**Example**: A fintech SaaS company undergoing a security audit needs to provide proof of compliance from their cloud infrastructure provider, and downloads a SOC 2 report from Artifact to attach to the audit materials.

### ☆☆☆ AWS Audit Manager
**Automated compliance evidence collection**

Audit Manager continuously and automatically collects configuration and activity evidence from your AWS environment, checking it against the requirements of a given compliance framework (GDPR, HIPAA, PCI-DSS, etc.) and generating compliance assessment reports automatically — sparing you the tedious manual work of screenshotting and organizing evidence by hand.

**Example**: A healthcare tech company needs to run periodic HIPAA compliance audits. They use Audit Manager to continuously track whether the relevant configurations meet requirements, and export a ready-made evidence report when audit season arrives.

### ★★★ Amazon Inspector
**Automated vulnerability scanning**

Inspector automatically scans EC2 instances and container images, checking for known software vulnerabilities (CVEs) and unintended network exposure, and provides a risk score along with remediation guidance. It runs continuously, proactively alerting you when a new high-severity vulnerability is discovered, instead of waiting for periodic manual scans.

**Example**: A team wires Inspector into their CI/CD pipeline so every new container image is automatically scanned at build time; if a high-severity vulnerability is found, that image is blocked from being deployed to production.

### ☆☆☆ AWS CloudHSM
**Dedicated hardware-level key management**

CloudHSM gives you a dedicated hardware security module (HSM) that meets strict compliance standards like FIPS 140-2, letting you generate, store, and manage encryption keys at the hardware level. It offers a higher level of compliance and isolation than KMS's software-managed keys, but at a higher cost and management overhead.

**Example**: A bank is required by regulation to keep its keys on dedicated hardware devices rather than a software-managed multi-tenant environment, so it chooses CloudHSM over standard KMS.

### ★☆☆ Amazon Detective
**Root-cause analysis for security incidents**

Detective automatically collects log data from multiple sources — VPC Flow Logs, CloudTrail, GuardDuty, and more — and builds it into a visual relationship graph, helping the security team quickly trace "how did this attack happen, and what resources did it touch" after an incident, significantly shortening the post-incident investigation time.

**Example**: After GuardDuty flags an anomalous login, the security team opens Detective and follows the graph to see exactly which resources that login touched and what actions it took afterward.

### ★☆☆ Amazon Cognito
**Authentication and authorization for application users**

*(Covered in depth this week on Day 6 — see section 2.3 below; omitted here.)*

### ☆☆☆ AWS Directory Service
**A managed directory service**

Directory Service provides a managed version of Microsoft Active Directory (or a lightweight AD-compatible directory), letting a company's existing directory setup extend directly into AWS instead of standing up a separate identity system just for cloud resources. It's commonly used when a company wants to preserve its existing AD-based identity model as it moves to the cloud.

**Example**: A company that previously used AD to manage all employee accounts and permissions extends that AD into AWS via Directory Service after moving to the cloud, so employees can use the same credentials to log into both on-prem systems and AWS resources.

### ★☆☆ AWS Firewall Manager
**Centralized security policy management across accounts**

Firewall Manager lets you configure and push out WAF rules, Security Group rules, Shield protections, and other security settings from one place, automatically applying them across every account and resource in your organization — avoiding the inconsistent security posture that comes from each team managing its own policies.

**Example**: A large enterprise with dozens of business units and hundreds of AWS accounts uses Firewall Manager to centrally push a baseline set of WAF rules to every account; newly created resources automatically inherit that rule set too.

### ★★★ Amazon GuardDuty
**Intelligent threat detection**

GuardDuty is a managed threat-detection service that continuously analyzes CloudTrail management events, VPC Flow Logs, DNS query logs, and other data sources, using machine learning and threat intelligence to spot anomalous behavior — like unusual API call patterns or communication with known-malicious IPs — without you having to build and maintain your own complex log-analysis pipeline.

**Example**: GuardDuty notices an EC2 instance suddenly communicating heavily with a known-malicious IP, concludes it may have been compromised, and automatically generates a high-severity alert so the security team can investigate right away.

### ★★★ AWS Shield
**DDoS protection**

Shield protects applications from Distributed Denial of Service (DDoS) attacks. The Standard tier is free and automatically protects every AWS customer at a basic level; the Advanced tier is paid and adds more sophisticated detection, real-time attack visibility, and access to a dedicated response team to help mitigate large-scale attacks.

**Example**: A public-facing e-commerce site is hit by a large-scale DDoS attack during a promotional event. Shield Advanced automatically detects and mitigates the attack traffic, and the site doesn't experience any noticeable outage.

### ★★☆ AWS IAM Identity Center (formerly AWS Single Sign-On)
**Enterprise single sign-on**

IAM Identity Center lets employees log in once with a single identity to access multiple AWS accounts, and it can extend to third-party SaaS application logins as well. It can integrate with an existing identity provider (like Azure AD), consolidating permission management and login into a single place — particularly valuable for large organizations with multiple AWS accounts.

**Example**: A company with 10 AWS accounts across different business lines used to require employees to remember 10 separate sets of login credentials. After rolling out IAM Identity Center, employees log in once and see every account they have access to.

### ★★★ AWS KMS
**Key management service**

KMS creates and manages the encryption keys used to protect data, and it underpins the at-rest encryption features across nearly every AWS service — S3, EBS, RDS, and more. It follows an envelope-encryption model: a master key encrypts a data key, and the data key encrypts the actual data. The master key can be AWS-managed, or a customer-managed key you create and control yourself (giving you more policy-level control).

**Example**: A company requires that all customer data in S3 be encrypted at rest, and wants control over who can use the decryption key, so they create a customer-managed key in KMS, configure the bucket to use it for encryption, and fine-tune the key's usage policy.

### ★☆☆ AWS Certificate Manager (ACM)
**Free SSL/TLS certificate management**

ACM issues and auto-renews SSL/TLS certificates for free, used to enable HTTPS on services like CloudFront and Application Load Balancer. Requesting and manually renewing certificates has traditionally been a tedious operational chore; ACM fully automates the process, renewing certificates before they expire with no manual intervention required.

**Example**: A website requests a free certificate from ACM at launch and attaches it to CloudFront. ACM automatically renews it before expiration, so the team never has to worry about a certificate lapse causing HTTPS errors on the site.

### ★☆☆ Amazon Macie
**Automated sensitive-data discovery**

Macie uses machine learning to automatically scan S3 buckets, identifying and classifying sensitive data inside them — personally identifiable information (PII), credit card numbers, credentials, and the like — and assigning an exposure risk score, helping companies avoid data compliance missteps.

**Example**: A company isn't sure exactly how much sensitive customer data is sitting in its S3 buckets, or whether any of it has been accidentally made public. A full Macie scan uncovers and lets them fix several accidentally public buckets.

### ☆☆☆ AWS Resource Access Manager (RAM)
**Cross-account resource sharing**

RAM lets you securely share certain AWS resources (subnets, Transit Gateways, licenses, etc.) with other accounts in your organization, instead of recreating them in every account — saving resources and simplifying centralized management.

**Example**: An enterprise has a dedicated networking account that owns a Transit Gateway. Using RAM, they share that gateway with a dozen or so business-unit accounts, which connect to it directly instead of each building their own networking infrastructure from scratch.

### ★★★ AWS Secrets Manager
**Storage and automatic rotation of credentials**

Secrets Manager is purpose-built for storing sensitive credentials like database passwords and API keys, and it supports configuring automatic periodic rotation — updating the corresponding database or service in sync with the rotation, with no manual password changes or reconfiguration needed. Application code never has to hardcode a password; it fetches the current value from Secrets Manager at runtime instead.

**Example**: An application's RDS database password rotates automatically every 90 days. Secrets Manager updates the RDS password configuration at the same time it rotates the secret, and the application fetches the latest password from Secrets Manager in real time before every connection — no manual step required.

### ★☆☆ AWS Security Hub
**A unified security posture dashboard**

Security Hub aggregates findings from multiple security services — GuardDuty, Inspector, Macie, and others — into a single dashboard, and checks them against industry security standards (like the CIS benchmark) to produce an overall security score and a prioritized to-do list, so the security team doesn't have to bounce between multiple service consoles.

**Example**: The security team opens the Security Hub dashboard every morning and sees, at a glance, every high-severity alert generated overnight — regardless of whether it came from GuardDuty or Inspector — and works through them by priority.

### ★★★ AWS WAF
**Web application firewall**

WAF filters HTTP/HTTPS traffic entering a web application or API based on rules you configure — blocking SQL injection, cross-site scripting, rate-limiting a single IP, and so on. It typically sits in front of CloudFront, an ALB, or API Gateway, intercepting malicious traffic and protecting the backend application from common web attacks.

**Example**: An API endpoint is found to be under frequent brute-force attack. The team configures a WAF rate-limiting rule in front of API Gateway, automatically blocking any single IP that exceeds a request-rate threshold in a short window.

### ★★★ AWS IAM
**The core identity and access management service**

*(Covered in depth this week on Day 4–5 — see section 2.2 below; omitted here.)*

## 2.2 This Week's Deep Dive: IAM (Day 4–5)

**① IAM policy evaluation logic (Day 4)**
- Five categories of policy together determine "effective permissions": identity policy, resource policy, SCP, permission boundary, session policy.
- Identity policies attach to a person/role (what can I do); resource policies attach to a resource (who can touch me), and are evaluated by **identity**, not by IP — which is also why EC2 doesn't support resource policies.
- SCPs and permission boundaries **only ever subtract** — they intersect with the identity policy and can only narrow what's allowed, never expand it.
- **An explicit Deny always wins**: if any layer explicitly states "deny," the result is "not allowed" no matter how many "allows" exist elsewhere.
- **Explicit deny vs. implicit deny**: the former is a policy stating "deny" in plain text; the latter is an operation that simply isn't covered by the intersection of any applicable policy. Same outcome, opposite troubleshooting direction.
- Why cross-account S3 access requires configuration on both sides: within the same account, the identity policy alone is enough; across accounts, both the identity policy and the resource policy must grant access.

**② Roles, STS, and credentials (Day 5)**
- IAM User is a long-lived identity; IAM Role is a borrowable identity template; STS is the service that issues temporary credentials.
- A role carries two documents: a **trust policy** (who's allowed to assume it) and a **permission policy** (what it can do once assumed).
- The AssumeRole flow: make the request → STS checks the trust policy → if eligible, issues a temporary credential set (15 minutes to 12 hours) → act using that role's identity → credentials expire and become invalid.
- **ExternalId**: used in cross-account scenarios (e.g., a SaaS vendor acting on behalf of multiple customers) to prevent a mixed-up role ARN from causing access to the wrong account.
- **EC2** uses an Instance Profile + IMDS; the SDK caches credentials on demand and refreshes them shortly before expiry — it's "fetched."
- **Lambda** uses an execution role; the Lambda service performs AssumeRole on your behalf before invocation and injects the credentials into the environment variables — it's "handed to you."
- Why production environments avoid long-lived access keys: the exposure window shrinks from "could go unnoticed for months" down to "expires automatically within hours at most," and every AssumeRole call is logged by CloudTrail for auditing.

## 2.3 This Week's Deep Dive: Cognito (Day 6)

> On star ratings: the course rates Cognito at ★☆☆ (a marginal item for the CCP exam), while the Phase 1 study plan bumps it up to ★★★. This isn't a contradiction — the evaluation criteria changed. The CCP exam doesn't test Cognito in much depth, but for an AI engineer building a GenAI application with a login flow, Cognito is standard equipment.

- **User Pool**: handles authentication ("who are you") — issues a JWT once login succeeds.
- **Identity Pool**: handles authorization/credential exchange ("what AWS permissions can you get") — exchanges the JWT with STS for temporary AWS credentials (essentially `AssumeRoleWithWebIdentity`, the same underlying mechanism as the AssumeRole from Day 5).
- Pure authentication only needs a User Pool; if the front end needs to touch AWS resources directly (uploading straight to S3 from the browser, calling Bedrock directly), you also need an Identity Pool.
- The three JWT tokens: **ID Token** (user attributes, proves "who you are"), **Access Token** (permission scope, lets an API decide whether to allow the request), **Refresh Token** (gets a new token set without requiring the user to log in again).
- API Gateway's three authorization modes: **Cognito Authorizer** (the simplest choice for a standard Cognito setup), **Lambda Authorizer** (for a custom identity system or complex logic), **IAM authorization** (when the caller is already an AWS identity).
- Key insight: the user's identity typically "gets off the bus" once it reaches the backend — Lambda calls Bedrock using **its own execution role**, not the user's identity. If you need per-user auditing, you have to manually parse the JWT to extract the user ID.
- Social login is essentially federating a third-party provider into the User Pool as a federated identity provider — everything ultimately converges into the same standardized JWT format.

## 2.4 Architecture / Flow Diagrams (Described in Text)

**IAM effective-permission formula**
```
Effective permissions = (identity policy ∪ resource policy) ∩ SCP ∩ permission boundary ∩ session policy
and ANY explicit Deny anywhere overrides everything else
```

**Full AssumeRole flow for borrowing a role**
```
Call AssumeRole → STS checks the role's trust policy (are you eligible)
→ if eligible, issues a temporary credential set → act using that role's identity (what you can do depends on the role's own permission policy)
→ expires, must be reborrowed
```

**User login → protected API call → backend calls Bedrock**
```
User logs in → User Pool authenticates, issues a JWT
→ frontend calls API Gateway (with the Access Token) → Cognito Authorizer validates the token
→ once validated, forwarded to Lambda → Lambda calls Bedrock using its own execution role (not the user's identity)
```

**Branch: frontend calling Bedrock directly, bypassing the backend**
```
JWT issued by User Pool → handed to Identity Pool → calls STS's AssumeRoleWithWebIdentity
→ exchanged for temporary AWS credentials → frontend uses those credentials to call Bedrock directly
```
