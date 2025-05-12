# Role Composition & Group Naming Strategy 

## Role Composition Strategy

Each **Platform Role** (group) is assigned to **multiple app roles across services**. 
Users added to the group automatically receive the appropriate access.


Example Services: 

| Service (App Registration) | Service Roles  (App Roles) |
|----------------------------|-----------------------|
| TRE Core                   | `TREUser`, `TREAdmin` |
| Access Requests            | `Reviewer`, `Requester` |
| Control Center              | `Admin`               |


Example Platform Roles: 

| Platform Role (Azure Security Group) | Service Roles  (App Roles)                                             |
|--------------------------------------|------------------------------------------------------------------------|
| Administrator                        | `TREAdmin`<br>`[Control Center] Admin`<br> `[Access Request] Reviewer` |
| Researcher                           | `TREAdmin`<br>`[Access Request] Requester`                              |


> Note that it’s helpful if App Role names are namespaced or clearly scoped to their service. For example, "Admin" could appear in multiple services, so "AccessRequests.Admin" or "CC.Admin" improves clarity.


---

## Scope: 

Note that we are **not including TRE Workspace roles** within Platform Roles since they are specific to individual workspaces and must be managed separately.  

---

 ## Group Naming Strategy 

Since we are using Azure Entra Security Groups for both platform roles and "customers" (organizations or companies), 
we need a clear naming convention and tagging strategy to disambiguate the two. 


**1. Naming conventions to disambiguate groups used for customers & platform roles** 

Using distinct, mandatory prefixes for each purpose:

| Purpose  | Prefix example  | Example group name |
|----------|-----------------|--------------------|
| Platform Role | PR_  |  PR_ADMIN, PR_RESEARCHER |
| Customer Group | CUST_  |CUST_ACME_CORP, CUST_NHS_UK |

- Use UPPER_SNAKE_CASE for consistency in display names
- This enables quick filtering (e.g. all CUST_ groups)

**2. Adding metadata** 

As seen above, the group names may help us disambiguate customers but the can also 

When creating a Security Group via Graph API, you can set additional properties:

```
{
  "displayName": "CUST_ACME_CORP",
  "mailNickname": "cust_acme_corp",
  "description": "Customer: ACME Corporation",
  "groupTypes": [],
  "mailEnabled": false,
  "securityEnabled": true
}
```

We propose:
- using the 'description' for the human-readable customer name.
- replace spaces with underscores & capitalize for the displayName for consistency in Azure listings.


**Alternative: use extensionAttributes for group type & metadata**

Alternatively, you could define custom directory schema extensions:

```
groupType = "platformRole" or "customer"
customerId = "acme" (for customer groups)
```

Reference: [Schema extensions in Microsoft Graph](https://learn.microsoft.com/en-us/graph/api/schemaextension-post-schemaextensions?view=graph-rest-1.0&tabs=http)

However, these are more complex to manage and query.  

----