### 👻 TODO
#### Upgrades
- **Page Actions**: expand page actions exposed via REST API.
- **Page Actions**: Fine-tuning existing methods.
- **Page Actions**: Custom script execution on page session - allow users to inject and execute custom JavaScript in each session’s context, offering flexibility for automation and interaction beyond basic navigation.

#### Features
- **Browsers scaling** - Monitor browser instances based on their load and capacity, scale up/down as needed.  

implement a browser pool where a limited number of browser instances are initialized at startup and reused across multiple sessions.
Each browser could host multiple pages, with each page representing an isolated session. This allows you to minimize memory usage while avoiding the need to frequently spin up and shut down browser instances.

- **Caching** - add Redis support.

#### API
##### Session Control Endpoints:
Create, retrieve, update, and delete sessions, each with its unique ID.
##### Script Execution Endpoint:
Accepts a script payload and executes it in the context of a specific session.
##### Session Persistence and Management:
Allow users to specify timeouts, enable session reuse, or clone sessions to handle multi-step workflows.
##### Resource and Monitoring Endpoints:
Provide insights on session resource usage, active users, and active browser instances.


#### Research
- Local storage of sessions (browsers)


##### for more info refer to this conversation with ChatGPT *https://chatgpt.com/share/672a9a49-9534-8010-825a-2c175d0edd9f*