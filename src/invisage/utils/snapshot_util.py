from invisage.schemas.pages import Snapshot


class SnapshotUtil:
    @classmethod
    async def capture_session_snapshot(cls, page) -> Snapshot:
        # Capture the URL
        snapshot = Snapshot()
        snapshot.url = page.url

        # 1. Capture cookies
        cookies = await page.cookies()
        snapshot.cookies = cookies

        # 2. Capture Local Storage
        local_storage = await page.evaluate(
            """() => {
            let ls = {};
            for (let i = 0; i < localStorage.length; i++) {
                let key = localStorage.key(i);
                ls[key] = localStorage.getItem(key);
            }
            return ls;
        }"""
        )
        snapshot.local_storage = local_storage

        # 3. Capture Session Storage
        session_storage = await page.evaluate(
            """() => {
            let ss = {};
            for (let i = 0; i < sessionStorage.length; i++) {
                let key = sessionStorage.key(i);
                ss[key] = sessionStorage.getItem(key);
            }
            return ss;
        }"""
        )
        snapshot.session_storage = session_storage

        # 4. Capture DOM State (basic example for input values)
        dom_state = await page.evaluate(
            """() => {
            let state = {};
            document.querySelectorAll("input, textarea, select").forEach(el => {
                state[el.name || el.id || el.tagName] = el.value;
            });
            return state;
        }"""
        )
        snapshot.dom_state = dom_state

        # 5. Capture Network Stack - save request and response details
        network_requests = []

        def save_request_response_data(request):
            async def handler(response):
                network_requests.append(
                    {
                        "url": request.url,
                        "method": request.method,
                        "headers": request.headers,
                        "request_post_data": await request.postData(),
                        "response_status": response.status,
                        "response_headers": response.headers,
                        "response_body": await response.text(),
                    }
                )

            return handler

        page.on("request", lambda req: req.continue_())
        page.on("response", lambda res: save_request_response_data(res.request)(res))

        # Intercept requests and responses
        await page.setRequestInterception(True)
        await page.goto(page.url, waitUntil="networkidle2")
        snapshot.network_requests = network_requests

        # 6. Capture Custom Scripts (optional) - Example of an executed script
        custom_scripts = []
        example_script = "document.body.style.backgroundColor = 'blue';"  # Example script
        await page.evaluate(example_script)
        custom_scripts.append(
            {
                "script": example_script,
                "state": await page.evaluate("document.body.style.backgroundColor"),
            }
        )
        snapshot.custom_scripts = custom_scripts

        # 7. Metadata
        snapshot.timestamp = str(await page.evaluate("new Date().toISOString()"))
        snapshot.user_agent = await page.evaluate("navigator.userAgent")
        snapshot.viewport_size = await page.viewportSize()

        # Return the complete snapshot
        return snapshot

    @classmethod
    async def restore_session(cls, page, snapshot: Snapshot):
        # Set the user agent to match the original session
        await page.setUserAgent(snapshot["user_agent"])

        # Set viewport size to match the original session
        if snapshot["viewport_size"]:
            width, height = snapshot["viewport_size"]["width"], snapshot["viewport_size"]["height"]
            await page.setViewport({"width": width, "height": height})

        # 1. Restore Cookies
        if "cookies" in snapshot:
            await page.setCookie(*snapshot["cookies"])

        # 2. Restore Local Storage
        if "local_storage" in snapshot:
            await page.goto(
                snapshot["url"], waitUntil="domcontentloaded"
            )  # Load page to access local storage
            await page.evaluate(
                f"""() => {{
                let ls = {snapshot['local_storage']};
                for (let key in ls) {{
                    localStorage.setItem(key, ls[key]);
                }}
            }}"""
            )

        # 3. Restore Session Storage
        if "session_storage" in snapshot:
            await page.evaluate(
                f"""() => {{
                let ss = {snapshot['session_storage']};
                for (let key in ss) {{
                    sessionStorage.setItem(key, ss[key]);
                }}
            }}"""
            )

        # 4. Restore DOM State (e.g., input field values)
        if "dom_state" in snapshot:
            dom_state_script = "(() => {"  # Start script definition
            for element, value in snapshot["dom_state"].items():
                # Modify each element by name/id/tag if exists
                dom_state_script += f"""
                    let el = document.querySelector("[name='{element}'], #{element}, {element}");
                    if (el) el.value = "{value}";
                """
            dom_state_script += "})()"
            await page.evaluate(dom_state_script)

        # 5. Replay Custom Scripts
        if "custom_scripts" in snapshot:
            for script in snapshot["custom_scripts"]:
                await page.evaluate(script["script"])

        # 6. Replay Network Requests (optional)
        # This is complex and may not be needed unless a specific API response affects state.
        # If replaying API requests is crucial, you could implement request interception
        # and respond with the saved request/response data in `network_requests`.
        await cls._intercept_requests(page, snapshot["network_requests"])

        # Visit the initial URL to restore the page
        await page.goto(snapshot["url"], waitUntil="networkidle2")

        # Ensure DOM state or other JavaScript adjustments have taken effect
        await page.waitFor(1000)

        # Here you could perform assertions or save a screenshot to verify restoration if needed
        # await page.screenshot({'path': 'restored_session.png'})
        ...

    @classmethod
    async def _intercept_requests(cls, page, network_requests: list):
        async def handle_request(request):
            # Match the request URL with saved data and respond with stored response if available
            for saved_request in network_requests:
                if (
                    request.url == saved_request["url"]
                    and request.method == saved_request["method"]
                ):
                    await request.respond(
                        {
                            "status": saved_request["response_status"],
                            "headers": saved_request["response_headers"],
                            "body": saved_request["response_body"],
                        }
                    )
                    return
            await request.continue_()  # Allow other requests to go through if no match

        await page.setRequestInterception(True)
        page.on("request", handle_request)
