from typing import Dict, List

from fastapi import APIRouter

from user_service.models.schemas import (CustomerCreateRequest, CustomerInfo,
                                         UserInfo)
from user_service.services.graph import graph_get, graph_post

router = APIRouter()

CUSTOMER_PREFIX = "CUST_"


@router.get("/", response_model=List[CustomerInfo])
async def list_customers():
    """
    List all customer groups (i.e., Entra security groups with names starting with 'CUST_').

    Returns
    -------
    List[Dict[str, str]]
        A list of customer groups with their ID and display name.
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
        if g["displayName"].startswith(CUSTOMER_PREFIX)
    ]


@router.post("/", response_model=Dict[str, str])
async def create_customer(payload: CustomerCreateRequest):
    """
    Create a new customer group using the CUST_ prefix.

    Parameters
    ----------
    request : CustomerCreateRequest
        Includes the name and optional description for the customer.

    Returns
    -------
    dict
        Details of the newly created group.
    """
    group_name = f"{CUSTOMER_PREFIX}{payload.name.upper()}"
    group_data = {
        "displayName": group_name,
        "mailNickname": group_name.lower().replace(" ", "_"),
        "description": payload.description or f"Customer group for {payload.name}",
        "securityEnabled": True,
        "mailEnabled": False,
        "groupTypes": [],
    }
    created = await graph_post("/groups", group_data)
    return {"id": created["id"], "displayName": created["displayName"]}


@router.get("/{customer_id}/users", response_model=List[UserInfo])
async def get_users_in_customer(customer_id: str):
    """
    List users assigned to a given customer group.

    Parameters
    ----------
    customer_id : str
        The object ID of the customer group.

    Returns
    -------
    List[UserInfo]
        A list of users assigned to the customer.
    """
    members = await graph_get(f"/groups/{customer_id}/members?$select=id,displayName,userPrincipalName")
    users = []
    for m in members.get("value", []):
        if m.get("@odata.type") == "#microsoft.graph.user":
            users.append(
                {
                    "id": m["id"],
                    "displayName": m["displayName"],
                    "userPrincipalName": m["userPrincipalName"],
                }
            )
    return users


@router.post("/{customer_id}/users/{user_id}")
async def assign_user_to_customer(customer_id: str, user_id: str):
    """
    Assign a user to a customer group.

    Parameters
    ----------
    customer_id : str
        The ID of the customer group.
    user_id : str
        The object ID of the user to assign.

    Returns
    -------
    dict
        A success message.
    """
    await graph_post(
        f"/groups/{customer_id}/members/$ref",
        {"@odata.id": f"https://graph.microsoft.com/v1.0/directoryObjects/{user_id}"},
    )
    return {"message": "User assigned to customer."}
