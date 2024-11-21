### 🌐🕹️ WebPilot - TODO
#### Feature/Functional Tasks
- **Testing**: write tests.
- **Rate Limiting - Redis**: implement Redis support.
- **Create Dockerfile**: create a ready-to-deploy dockerfile for most use cases.
- **Page Session - Redis**: implement Redis storage of page session objects. (use json)

#### API Functionality Road-map
##### Session Control Endpoints:
- **DONE** - Create, retrieve, update, and delete sessions, each with its unique ID.
##### Script Execution Endpoint:
- **DONE** - Accepts a script payload and executes it in the context of a specific session.
##### Session Persistence and Management:
- Allow users to specify timeouts, enable session reuse, or clone sessions to handle multi-step workflows.
##### Resource and Monitoring Endpoints:
- **DONE** - Provide insights on session resource usage and active browser instances.