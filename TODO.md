### 🌐🕹️ WebPilot - TODO
#### Tasks
- **Exception handling**: move exception handling methods to app module (handle globally).
- **Page Actions**: expand page actions exposed via REST API.
- **Snapshots**: validate robust methods working as expected.
- **Testing**: write tests.
- **db**: implement a nosql db for storing session snapshots.
- **scaling**: finish implementing logic for scaling browser pools (based on category).
- **Browser pools logic**: user creates a pool with set configurations for the browser within the pool. and then the pool itself is what scales when a set threshold is exceeded. it is abstracted from the user. and thus the user wont care about the browsers within the pool.
- **Page functionality**: add ability to set Geo-location on page session.
- **Update .env.default**
- **LeasedBrowser**: implement is_busy() method to check if browser has any pages or idle.
- **LeasedBrowser**: implement has_capacity() method to check if browser has capacity for new page.

#### API
##### Session Control Endpoints:
Create, retrieve, update, and delete sessions, each with its unique ID.
##### Script Execution Endpoint:
Accepts a script payload and executes it in the context of a specific session.
##### Session Persistence and Management:
Allow users to specify timeouts, enable session reuse, or clone sessions to handle multi-step workflows.
##### Resource and Monitoring Endpoints:
Provide insights on session resource usage, active users, and active browser instances.
