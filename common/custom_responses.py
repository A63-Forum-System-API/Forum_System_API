from fastapi import Response
from starlette.responses import JSONResponse


class BadRequest(JSONResponse):
    def __init__(self, content=''):
        super().__init__(status_code=400, content={"detail": content})

class Locked(JSONResponse):
    def __init__(self, content=''):
        super().__init__(status_code=400, content={"detail": f"This {content} is locked"})

class Unauthorized(JSONResponse):
    def __init__(self, content=''):
        super().__init__(status_code=401, content={"detail": content})

class ForbiddenAccess(JSONResponse):
    def __init__(self, content="User does not have access to this category"):
        super().__init__(status_code=403, content={"detail": content})

class NotFound(JSONResponse):
    def __init__(self, content=''):
        super().__init__(status_code=404, content={"detail": f"{content} not found"})

class OK(JSONResponse):
    def __init__(self, content=''):
        super().__init__(status_code=200, content={"detail": content})

class Created(JSONResponse):
    def __init__(self, content=''):
        super().__init__(status_code=201, content={"detail": content})

class NoContent(Response):
    def __init__(self):
        super().__init__(status_code=204)