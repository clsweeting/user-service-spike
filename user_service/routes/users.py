from fastapi import APIRouter
from typing import List
from user_service.models.schemas import PlatformRole, UserInfo
from user_service.services.graph import graph_get

router = APIRouter()


@router.get(
    "/",
    response_model=List[UserInfo],
    description="Returns all user accounts in Entra ID, excluding non-user directory objects like service principals or contacts."
)
async def list_users():
    """
    Retrieve a list of all user accounts in the Entra directory.

    Returns
    -------
    List[UserInfo]
        A list of user objects, each containing `id`, `displayName`, and `userPrincipalName`.

    Notes
    -----
    This endpoint filters out non-user directory objects using the `@odata.type` field to ensure
    only returns real user objects are returned and not other directory objects (like groups, service principals,
    or shared mailboxes) that might sneak in under certain Graph API configurations.
    """
    data = await graph_get("/users?$select=id,displayName,userPrincipalName")
    return [
        {
            "id": u["id"],
            "displayName": u["displayName"],
            "userPrincipalName": u["userPrincipalName"]
        }
        for u in data.get("value", [])
        if "@odata.type" not in u or u["@odata.type"] == "#microsoft.graph.user" # defensive filter
    ]


@router.get(
    "/{user_id}/platform-roles",
            response_model=List[str],
            description="Returns the platform roles (i.e., Entra groups) the given user is a member of. Only direct group memberships are returned."
)
async def get_user_platform_roles(user_id: str):
    """
    Retrieve the list of platform roles (groups) that a given user is a member of.

    Parameters
    ----------
    user_id : str
        The unique object ID of the user in Entra ID.

    Returns
    -------
    List[str]
        A list of display names for the groups the user belongs to.

    Notes
    -----
    This uses Microsoft Graph's `/users/{id}/memberOf` to resolve group membership.
    Only direct memberships are returned; nested groups are not expanded.
    """
    groups = await graph_get(f"/users/{user_id}/memberOf")
    return [g["displayName"] for g in groups.get("value", []) if "displayName" in g]

