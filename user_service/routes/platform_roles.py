from typing import Dict, List, Any

from fastapi import APIRouter

from user_service.models.schemas import PlatformRole, PlatformRoleUpdate, UserInfo
from user_service.services.graph import graph_delete, graph_get, graph_post

router = APIRouter()

PLATFORM_ROLE_PREFIX = "PR_"


@router.get("/", response_model=List[PlatformRole])
async def list_platform_roles():
    """
    Retrieve a list of all platform roles defined as Entra ID groups.

    Returns
    -------
    List[PlatformRole]
        A list of group objects, each containing `id` and `displayName`.

    Notes
    -----
    Platform roles are modeled as Azure Entra security groups.
    This call uses the Microsoft Graph `/groups` endpoint with selected fields only.
    """
    data = await graph_get("/groups?$select=id,displayName")
    return [
        {
            "id": g["id"],
            "displayName": g["displayName"],
            "mailNickname": g.get("mailNickname", ""),
            "description": g.get("description", ""),
        }
        for g in data.get("value", [])
        if g["displayName"].startswith(PLATFORM_ROLE_PREFIX)
    ]


@router.get("/{role_id}/service-roles", response_model=Dict[str, List[Dict[str, str]]])
async def get_service_roles_for_platform_role(role_id: str):
    """
    Retrieve all service role assignments for a given platform role (group).

    Returns
    -------
    Dict[str, List[Dict[str, str]]]
        A dictionary mapping each application (by name) to a list of app role objects,
        including both role `value` and `displayName`.
    """
    assignments = await graph_get(f"/groups/{role_id}/appRoleAssignments")
    result: dict[str, Any] = {}

    for a in assignments.get("value", []):
        app_name = a.get("resourceDisplayName", "Unknown App")
        app_role_id = a.get("appRoleId")
        resource_id = a.get("resourceId")

        # Lookup appRoles from the service principal
        sp = await graph_get(f"/servicePrincipals/{resource_id}")
        roles_by_id = {
            r["id"]: {
                "id": r["id"],
                "value": r.get("value", "(unnamed)"),
                "displayName": r.get("displayName", r.get("value", "(unnamed)")),
            }
            for r in sp.get("appRoles", [])
        }

        role = roles_by_id.get(
            app_role_id,
            {
                "id": app_role_id,
                "value": "unknown",
                "displayName": "Unknown or Deleted Role",
            },
        )

        result.setdefault(app_name, []).append(role)

    return result


@router.get("/{role_id}/users", response_model=List[UserInfo])
async def get_users_in_platform_role(role_id: str):
    """
    Retrieve all users who are direct members of the given platform role group.

    Parameters
    ----------
    role_id : str
        The object ID of the Entra group representing a platform role.

    Returns
    -------
    List[UserInfo]
        A list of user objects, each including `id`, `displayName`, and `userPrincipalName`.

    Notes
    -----
    - This returns only direct members of the group, not transitive (nested) memberships.
    - Non-user members (e.g., service principals or other groups) are excluded.
    """
    members = await graph_get(f"/groups/{role_id}/members?$select=id,displayName,userPrincipalName")
    users = []
    for m in members.get("value", []):
        if m["@odata.type"] == "#microsoft.graph.user":
            users.append(
                {
                    "id": m["id"],
                    "displayName": m["displayName"],
                    "userPrincipalName": m["userPrincipalName"],
                }
            )
    return users


@router.post("/{role_id}/users")
async def add_user_to_platform_role(role_id: str, payload: Dict[str, str]):
    """
    Add a user to a platform role (i.e., to the specified Entra group).

    Parameters
    ----------
    role_id : str
        The ID of the group.
    payload : dict
        Must contain `user_id` as the Azure AD user object ID.

    Returns
    -------
    dict
        A success message if the operation completes.
    """

    @router.post("/{role_id}/users/{user_id}")
    async def add_user_to_platform_role(role_id: str, user_id: str):
        """
        Add a user to a platform role (i.e., to the specified Entra group).

        Parameters
        ----------
        role_id : str
            The ID of the group.
        user_id : str
            The object ID of the user to add.

        Returns
        -------
        dict
            A success message if the operation completes.
        """
        await graph_post(
            f"/groups/{role_id}/members/$ref",
            {"@odata.id": f"https://graph.microsoft.com/v1.0/directoryObjects/{user_id}"},
        )

        return {"message": "User added to platform role."}


@router.delete("/{role_id}/users/{user_id}")
async def remove_user_from_platform_role(role_id: str, user_id: str):
    """
    Remove a user from a platform role (i.e., from the specified Entra group).

    Parameters
    ----------
    role_id : str
        The ID of the group.
    user_id : str
        The object ID of the user to remove.

    Returns
    -------
    dict
        A success message if the operation completes.
    """
    await graph_delete(f"/groups/{role_id}/members/{user_id}/$ref")
    return {"message": "User removed from platform role."}


@router.put("/users/{user_id}/platform-role")
async def update_user_platform_role(user_id: str, update: PlatformRoleUpdate):
    """
    Update a user's platform role by removing them from one group and adding to another.

    Parameters
    ----------
    user_id : str
        The Azure AD object ID of the user.
    update : PlatformRoleUpdate
        Contains `from_role_id` and `to_role_id`.

    Returns
    -------
    dict
        A message confirming the role update.
    """
    await remove_user_from_platform_role(update.from_role_id, user_id)
    await add_user_to_platform_role(update.to_role_id, {"user_id": user_id})
    return {"message": "User's platform role updated."}
