## 📜 COMPLIANCE.md
### GreenGrid-Telco — GDPR & 3GPP Compliance Matrix
### 1. Compliance Positioning Statement

>GreenGrid-Telco is an infrastructure energy and climate observability platform.
>It does not process subscriber communications, personal user content, or network payload traffic.
>All analytics are performed on infrastructure-level telemetry, in accordance with GDPR Privacy by Design principles and 3GPP network security boundaries.


### 2. GDPR Compliance Matrix
| GDPR Principle                  | Relevant Article      | GreenGrid-Telco Implementation                                               |
| ------------------------------- | --------------------- | ---------------------------------------------------------------------------- |
| Lawfulness & Purpose Limitation | Art. 5(1)(a)(b)       | Data collected solely for energy, environment, and infrastructure operations |
| Data Minimization               | Art. 5(1)(c)          | Only telemetry metrics (kWh, temperature, runtime); no personal data         |
| Accuracy                        | Art. 5(1)(d)          | Direct measurement from certified meters and sensors                         |
| Storage Limitation              | Art. 5(1)(e)          | Configurable retention (raw vs aggregated data)                              |
| Integrity & Confidentiality     | Art. 5(1)(f), Art. 32 | TLS encryption, certificate-based authentication                             |
| Privacy by Design & Default     | Art. 25               | Edge-first processing, anonymization before transmission                     |
| Accountability                  | Art. 5(2)             | Audit logs, reproducible metrics, transparent algorithms                     |

### 3. Data Classification Policy
| Data Class    | Example                  | Handling                         |
| ------------- | ------------------------ | -------------------------------- |
| Non-PII       | Power usage, temperature | Stored & aggregated              |
| Pseudonymous  | Site ID                  | Hashed before uplink             |
| Sensitive     | Precise geo-location     | Precision configurable / reduced |
| Personal Data | Subscriber data          | **Not collected**                |



### 4. Data Retention Policy (Default)
| Data Type          | Retention                 |
| ------------------ | ------------------------- |
| Raw edge telemetry | 7–30 days                 |
| Aggregated metrics | 12–36 months              |
| ESG / SDG reports  | As required by regulation |



### 5. 3GPP / Telco Compliance Matrix
| Telco Requirement          | GreenGrid-Telco Alignment                        |
| -------------------------- | ------------------------------------------------ |
| MEC-style Edge Compute     | Edge gateways deployed at network-adjacent sites |
| Network Boundary Respect   | No access to RAN/Core payload traffic            |
| OSS/BSS Compatibility      | SNMP, Osmocom, standard OSS interfaces           |
| Security Architecture      | TLS, mutual authentication                       |
| Lawful Interception Safety | Explicitly outside LI path                       |
| Vendor Neutrality          | Multi-vendor energy & cooling support            |


### 6. Explicit Non-Goals
- GreenGrid-Telco does NOT:
- Perform lawful interception
- Inspect signaling payloads
- Track subscriber behavior
- Perform surveillance or identity recognition
