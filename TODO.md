### 🕸️👻 TODO
#### Upgrades
- **Page Actions**: expand page actions exposed via REST API.
- **Page Actions**: Fine-tuning existing methods.
- **Page Actions**: Custom script execution on page session - allow users to inject and execute custom JavaScript in each session’s context, offering flexibility for automation and interaction beyond basic navigation.

#### Features
- **Session SnapShot** - Support session snapshots to save state, enabling resumption or replication of specific sessions.  

Adding snapshot capabilities could be a powerful feature. You might allow users to save the current state of a session (including cookies, local storage, and page state) as a snapshot, then reload it later. This could be useful for long workflows or intermittent automation tasks.
By storing these snapshots in a cache or database, users could restore the session at a later time, maintaining continuity without needing to repeat previous steps.  
```python
# Example implementation
async def save_snapshot(page):
    cookies = await page.cookies()
    local_storage = await page.evaluate("Object.assign({}, window.localStorage)")
    session_storage = await page.evaluate("Object.assign({}, window.sessionStorage)")
    url = page.url

    snapshot = {
        "cookies": cookies,
        "local_storage": local_storage,
        "session_storage": session_storage,
        "url": url
    }
    return snapshot

async def restore_snapshot(browser, snapshot):
    page = await browser.newPage()
    # Set cookies
    await page.setCookie(*snapshot['cookies'])
    # Set local storage and session storage
    await page.goto("about:blank")  # Needed to access storage APIs in Pyppeteer
    await page.evaluate(f"Object.assign(window.localStorage, {snapshot['local_storage']})")
    await page.evaluate(f"Object.assign(window.sessionStorage, {snapshot['session_storage']})")
    # Navigate to saved URL
    await page.goto(snapshot['url'])
    return page
```

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