import asyncio
import logging
import random

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from sse_starlette.sse import EventSourceResponse

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)


COUNTER = {"#of_news": 0, "#of_subscribers": 0}


async def event_generator(request):
    """Generate status events with current # of users or news"""
    while True:
        if await request.is_disconnected():
            logger.debug("Request disconnected")
            break
        event = random.choice(["#of_news", "#of_subscribers"])
        COUNTER[event] += 1
        yield {
            "event": event,
            "retry": 5000,  # miliseconds
            "data": str(COUNTER[event]),  # HTML representation
        }
        logger.debug(f"{event}: {COUNTER[event]}")
        await asyncio.sleep(0.3)  # in seconds


app = FastAPI()


@app.get("/")
async def home():
    return HTMLResponse(
        """
<html>
  <head>
    <script src="https://unpkg.com/htmx.org@1.4.1"></script>
  </head>
  <body hx-sse="connect:/status_updates">
    <h1>&lt;/&gt;htmx and SSE with FastAPI</h1>
    <table>
      <tr>
        <td>News</td>
        <td hx-sse="swap:#of_news">0</td>
      </tr>
      <tr>
        <td>Operating</td>
        <td>24/7</td>
      </tr>
      <tr>
        <td>Subscribers</td>
        <td hx-sse="swap:#of_subscribers">0</td>
      </tr>
    </table>
  </body>
</html>
"""
    )


@app.get("/status_updates")
async def runStatus(request: Request):
    return EventSourceResponse(event_generator(request))
