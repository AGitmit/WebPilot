# async def page_usage_metrics(self):
#     # gather and view usage of resources for current visited host
#     # Create a single CDP session
#     cdp_client = await self.page.target.createCDPSession()
#     metrics = await cdp_client.send("Performance.getMetrics")
#     storage = await cdp_client.send("Storage.getUsageAndQuota", {
#     "origin": self.page.url
#     })
