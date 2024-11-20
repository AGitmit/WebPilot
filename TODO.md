### 🌐🕹️ WebPilot - TODO
#### Feature/Functional Tasks
- **Snapshots**: validate robust methods working as expected.
    - **db**: implement a nosql db for storing session snapshots.
- **Testing**: write tests.
- **Rate Limiting - Redis**: implement Redis support.
- **Page Session Cloning**: implement the ability to clone an existing session and return its session_id.
- **Create Dockerfile**: create a ready-to-deploy dockerfile for most use cases.

#### API Functionality Road-map
##### Session Control Endpoints:
- **DONE** - Create, retrieve, update, and delete sessions, each with its unique ID.
##### Script Execution Endpoint:
- **DONE** - Accepts a script payload and executes it in the context of a specific session.
##### Session Persistence and Management:
- Allow users to specify timeouts, enable session reuse, or clone sessions to handle multi-step workflows.
##### Resource and Monitoring Endpoints:
- **DONE** - Provide insights on session resource usage and active browser instances.