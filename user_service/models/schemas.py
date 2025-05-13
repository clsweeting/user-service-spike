from pydantic import BaseModel


class GroupInfo(BaseModel):
    id: str
    displayName: str
    mailNickname: str
    description: str


class PlatformRole(GroupInfo):
    pass


class CustomerInfo(GroupInfo):
    pass


class CustomerCreateRequest(BaseModel):
    name: str
    description: str = ""


class UserInfo(BaseModel):
    id: str
    displayName: str
    userPrincipalName: str


class PlatformRoleUpdate(BaseModel):
    from_role_id: str
    to_role_id: str
