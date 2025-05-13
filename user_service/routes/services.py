from typing import Dict, List

from fastapi import APIRouter

from user_service.services.graph import graph_get

router = APIRouter()


@router.get("/", response_model=List[Dict[str, str]])
async def list_services_with_roles():
    """
    List all Azure Entra service principals that define at least one App Role.
    """
    services_with_roles = []

    # Get all service principals with paging
    next_url = "/servicePrincipals?$top=50"

    while next_url:
        page = await graph_get(next_url)
        for sp in page.get("value", []):
            # Get full Service Principal record
            full_sp = await graph_get(f"/servicePrincipals/{sp['id']}")
            roles = full_sp.get("appRoles", [])
            if any(r.get("isEnabled", True) for r in roles):
                services_with_roles.append(
                    {
                        "id": full_sp["id"],
                        "displayName": full_sp.get("displayName", ""),
                        "appId": full_sp.get("appId", ""),
                    }
                )

        # Check for pagination
        next_url = page.get("@odata.nextLink", None)
        if next_url and next_url.startswith("https://graph.microsoft.com/v1.0"):
            next_url = next_url.replace("https://graph.microsoft.com/v1.0", "")

    return services_with_roles


@router.get("/{service_id}/roles", response_model=List[Dict[str, str]])
async def get_roles_for_service(service_id: str):
    """
    Get all App Roles defined in a specific service principal.

    Parameters
    ----------
    service_id : str
        The object ID of the service principal.

    Returns
    -------
    List[Dict[str, str]]
        Each role includes `id`, `value`, and `displayName`.
    """
    sp = await graph_get(f"/servicePrincipals/{service_id}")
    roles = sp.get("appRoles", [])
    return [
        {
            "id": r["id"],
            "value": r.get("value", "(unnamed)"),
            "displayName": r.get("displayName", r.get("value", "(unnamed)")),
        }
        for r in roles
        if r.get("isEnabled", True)
    ]
