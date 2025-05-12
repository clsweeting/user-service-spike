# Microsoft Graph API GUIDs. 

Where did those IDs come from in [graph-permissions.json](../graph-permissions.json) ? 

They're based on Microsoft’s **well-known service principal** for Microsoft Graph.

Reference: [Microsoft Graph Permissions Reference](https://learn.microsoft.com/en-us/graph/permissions-reference) lists all delegated and application permissions for Graph, including IDs. Look under Application permissions for each API (e.g., Group, Directory, AppRoleAssignment).

Alternatively, list them using: 

```bash 
az ad sp show --id 00000003-0000-0000-c000-000000000000 --query "appRoles[].{Name:value, ID:id}" -o table
```

The IDs used in our case: 

| Permission                      | ID                                   |
|---------------------------------|--------------------------------------|
| `Group.ReadWrite.All`             | 62a82d76-70ea-41e2-9197-370581804d09 | 
| `Directory.ReadWrite.All`         | 19dbc75e-c2e2-444c-a770-ec69d8559fc7 |
| `AppRoleAssignment.ReadWrite.All` | 06b708a9-e830-4db3-a914-8e69da51d44f |

These will not change between tenants — they’re globally consistent across Azure.
