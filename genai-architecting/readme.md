## Functional Requirements

The platform aims to enhance language learning by providing personalized, AI-driven study activities. It should support real-time interactions, offer feedback, and adapt to individual learning paces. The system must handle concurrent usage by approximately 100 active students located in Berlin. Given concerns about user data privacy and the rising costs of managed GenAI services, the company plans to invest in owning their infrastructure. They are considering an AI PC with a budget of €4,000 to €7,000 to support this initiative.

## Assumptions

The system assumes an open-source LLM will deliver real-time performance within a €4,000 to €7,000 hardware budget. Existing internet infrastructure should support 100 concurrent users without latency issues. Minimal model fine-tuning will suffice, and internal IT can handle server operations and security.

## Data Strategy

User input and session data will be securely stored in a centralized database, with core vocabulary indexed for fast retrieval. Encryption will protect data in transit and at rest, ensuring GDPR compliance. Cached data will reduce query response times, while anonymized data will support AI optimization.

## Considerations

Cost, performance, and scalability must be balanced due to budget limitations. Open-source models with traceable training data are prioritized to avoid licensing risks.