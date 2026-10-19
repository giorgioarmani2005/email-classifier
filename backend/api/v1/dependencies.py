from fastapi import Response, Request


def set_cookie(request: Request, response: Response) -> str:
    client_id = request.cookies.get("client_id")
    if not client_id:
        import uuid
        client_id = str(uuid.uuid4())
        response.set_cookie(key="client_id", value=client_id, httponly=True)
    return client_id
