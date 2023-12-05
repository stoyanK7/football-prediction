"""API endpoints for streaming logfiles to the client."""
from fastapi import APIRouter, Request
from sse_starlette import EventSourceResponse

from src.api.service import logfile_generator

router = APIRouter(prefix='/logfiles')


@router.get('/stream', response_class=EventSourceResponse)
async def stream_logfile(request: Request, logfile: str):
    """Stream a logfile to the client."""
    return EventSourceResponse(logfile_generator(request, logfile))
