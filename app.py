import asyncio
from itertools import count
import logging
import random

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from sse_starlette.sse import EventSourceResponse

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)


async def event_generator(request):
    """Generate status events with current # of users or news
    """
    for i in count():
        if await request.is_disconnected():
            logger.debug("Request disconnected")
            break
        event = random.choice(["#of_news", "#of_subscribers"])
        status = f"{i}"
        yield {
            "event": event,
            "retry": 30000,  # miliseconds
            "data": status,  # HTML representation
        }
        logger.debug(f"{event}: {status}")
        await asyncio.sleep(2)  # in seconds


app = FastAPI()


@app.get("/")
async def home():
    return HTMLResponse("""
<html>
  <head>
    <script src="https://unpkg.com/htmx.org@1.4.1"></script>
  </head>
  <body hx-sse="connect:/status_updates">
    <h1>&lt;/&gt;htmx and SSE with FastAPI</h1>
    <table>
      <tr>
        <td>News</td>
        <td hx-sse="swap:#of_news">?</td>
      </tr>
      <tr>
        <td>Operating</td>
        <td>24/7</td>
      </tr>
      <tr>
        <td>Subscribers</td>
        <td hx-sse="swap:#of_subscribers">??</td>
      </tr>
    </table>
  </body>
</html>
""")


@app.get("/status_updates")
async def runStatus(request: Request):
    return EventSourceResponse(event_generator(request))
