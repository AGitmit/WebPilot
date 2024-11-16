### 🌐🕹️ WebPilot - TODO
#### Feature/Functional Tasks
- **Page Actions**: make pydantic validate each of the allowed action's args instread of simply allowing **kwargs.
- **Snapshots**: validate robust methods working as expected.
- **Testing**: write tests.
- **db**: implement a nosql db for storing session snapshots.
- **Scaling browser pools**: Implement scaling up and down + ttl on browsers to detect browsers for scale down deletion.
- **Rate Limiting**: implement Redis support.

#### API tasks
##### Session Control Endpoints:
- Create, retrieve, update, and delete sessions, each with its unique ID.
##### Script Execution Endpoint:
- Accepts a script payload and executes it in the context of a specific session.
##### Session Persistence and Management:
- Allow users to specify timeouts, enable session reuse, or clone sessions to handle multi-step workflows.
##### Resource and Monitoring Endpoints:
- Provide insights on session resource usage, active users, and active browser instances.
