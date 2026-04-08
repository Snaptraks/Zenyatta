import random

import config


async def random_gif(http_session, query):
    """Return a random gif related to the query."""

    limit = 10
    params = {
        "q": query,
        "limit": limit,
        "media_filter": "gif",
        "contentfilter": "high",
        "locale": "en",
        "random": "true",
    }
    resp = await _klipy_endpoint(http_session, "search", params)
    resp = resp.get("results", [])
    if resp:
        random_gif = random.choice(resp)
        gif_url = random_gif["url"]
        return gif_url
    else:
        return None


async def _tenor_endpoint(http_session, endpoint, params):
    """Get a gif from Tenor"""

    query = params["q"].split()
    params["key"] = config.tenor_api_key
    if len(query) >= 1:
        async with http_session.get(
            f"https://api.tenor.com/v1/{endpoint}", params=params
        ) as resp:
            if resp.status == 200:
                try:
                    json_resp = await resp.json()
                    return json_resp
                except Exception:
                    pass
    return {}


async def _klipy_endpoint(http_session, endpoint, params):
    """Get a gif from Klipy"""

    query = params["q"].split()
    params["key"] = config.klipy_api_key
    if len(query) >= 1:
        async with http_session.get(
            f"https://api.klipy.com/v2/{endpoint}", params=params
        ) as resp:
            if resp.status == 200:
                try:
                    json_resp = await resp.json()
                    return json_resp
                except Exception:
                    pass
    return {}
