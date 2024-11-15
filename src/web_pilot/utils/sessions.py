from web_pilot.exc import InvalidSessionIDError


def break_session_id_to_parts(session_id: str) -> tuple:
    try:
        pool_id, browser_id, page_id = session_id.split("_")
        return (pool_id, browser_id, page_id)

    except ValueError:
        raise InvalidSessionIDError("Invalid session ID")
