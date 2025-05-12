import os
import httpx

from dotenv import load_dotenv

from cachetools import TTLCache
from cachetools.keys import hashkey


if not os.getenv("AZURE_CLIENT_ID"):
    load_dotenv()

# Settings - you can replace these with environment variables or a config loader
TENANT_ID = os.getenv("AZURE_TENANT_ID")
CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
GRAPH_API = "https://graph.microsoft.com/v1.0"


# Using TTLCache - Thread-safe for simple single-process FastAPI apps
# Cache for 3600s (1 hour), with maxsize=1 since we only need one token
token_cache = TTLCache(maxsize=1, ttl=3600)


def token_cache_key():
    """
    Generate a cache key for the Graph API token.

    Returns
    -------
    hashkey
        A hashable key used to store and retrieve the token from the TTL cache.
    """
    return hashkey("graph_token")


async def get_access_token() -> str:
    """
    Retrieve a Microsoft Graph API access token using client credentials.

    Returns
    -------
    str
        A bearer token to authorize subsequent Graph API requests.

    Notes
    -----
    - The token is cached in-memory using TTLCache for 1 hour (3600 seconds).
    - This avoids repeated calls to the token endpoint, reducing latency and quota usage.
    - If the token is not present or has expired, a new one is fetched via the `/token` endpoint.
    """
    key = token_cache_key()
    token = token_cache.get(key)
    if token:
        return token

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token",
            data={
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "scope": "https://graph.microsoft.com/.default",
                "grant_type": "client_credentials"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        response.raise_for_status()
        token = response.json()["access_token"]
        token_cache[key] = token
        return token


async def graph_get(endpoint: str) -> dict:
    """
    Perform a GET request to the Microsoft Graph API with bearer token authorization.

    Parameters
    ----------
    endpoint : str
        The relative endpoint path to call, e.g. `/users`, `/groups/{id}/members`.

    Returns
    -------
    dict
        The parsed JSON response from the Graph API.

    Raises
    ------
    httpx.HTTPStatusError
        If the Graph API request fails with a 4xx or 5xx error.
    """
    token = await get_access_token()
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{GRAPH_API}{endpoint}",
            headers={"Authorization": f"Bearer {token}"}
        )
        response.raise_for_status()
        return response.json()



async def graph_post(endpoint: str, json: dict) -> dict:
    """
    Perform a POST request to the Microsoft Graph API with bearer token authorization.

    Parameters
    ----------
    endpoint : str
        The relative endpoint path to call, e.g. `/groups/{id}/members/$ref`.
    json : dict
        The JSON body to send in the request.

    Returns
    -------
    dict
        The parsed JSON response from the Graph API, or empty if no content.

    Raises
    ------
    httpx.HTTPStatusError
        If the request fails.
    """
    token = await get_access_token()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{GRAPH_API}{endpoint}",
            json=json,
            headers={"Authorization": f"Bearer {token}"}
        )
        response.raise_for_status()
        return response.json() if response.content else {}



async def graph_delete(endpoint: str) -> None:
    """
    Perform a DELETE request to the Microsoft Graph API with bearer token authorization.

    Parameters
    ----------
    endpoint : str
        The relative endpoint path to call, e.g. `/groups/{id}/members/{user_id}/$ref`.

    Raises
    ------
    httpx.HTTPStatusError
        If the request fails.
    """
    token = await get_access_token()
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{GRAPH_API}{endpoint}",
            headers={"Authorization": f"Bearer {token}"}
        )
        response.raise_for_status()
