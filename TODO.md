### 👨‍✈️ TODO
#### Upgrades
- **Page Actions**: expand page actions exposed via REST API.
- **Page Actions**: Fine-tuning existing methods.

#### Features
- **db** - implement a nosql db for storing session snapshots.

#### API
##### Session Control Endpoints:
Create, retrieve, update, and delete sessions, each with its unique ID.
##### Script Execution Endpoint:
Accepts a script payload and executes it in the context of a specific session.
##### Session Persistence and Management:
Allow users to specify timeouts, enable session reuse, or clone sessions to handle multi-step workflows.
##### Resource and Monitoring Endpoints:
Provide insights on session resource usage, active users, and active browser instances.
