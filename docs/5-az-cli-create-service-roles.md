# Create the Service Roles using AZ CLI 

An idempotent script - [create_service_roles.sh](../create_service_roles.sh) - is provided to create hypothetical Service Roles (i.e. Azure App Registrations with App Roles assigned), and then assign them to Platform Roles (represented by security groups).

The script: 
1.	Registers two apps
2.	Adds two App Roles to each
3.	Creates two Platform Role groups
4.	Assigns App Roles from each app to those groups

NB: It assumes you’re signed in (`az login`) and have sufficient privileges.

If you prefer to do this step-by-step manually, individual scripts are provided below (non-idempotent):

-----

## 1. Register Two Apps 

Create two App Registrations - one for a Cohort Builder API, and one for a Data Access Request API: 

```bash 
APP1_NAME="Data Access Requests API"
APP2_NAME="Cohort Builder API"

APP1_ID=$(az ad app create --display-name "$APP1_NAME" --query appId -o tsv)
APP2_ID=$(az ad app create --display-name "$APP2_NAME" --query appId -o tsv)
```

Wait a minute for the service principals to be created then: 

```bash 
# Get object IDs of the service principals (needed for app role assignment)
SP1_ID=$(az ad sp show --id "$APP1_ID" --query id -o tsv)
SP2_ID=$(az ad sp show --id "$APP2_ID" --query id -o tsv)

echo "App1 ID: $APP1_ID"
echo "App2 ID: $APP2_ID"
echo "SP1 ID: $SP1_ID"
echo "SP2 ID: $SP2_ID"
```

----

## 2. Add App Roles to each app 

For the Data Access Requests API: 

```bash 
APP_ROLE1=$(cat <<EOF
[
  {
    "allowedMemberTypes": ["User", "Application"],
    "description": "Review data access requests",
    "displayName": "Reviewer",
    "id": "$(uuidgen)",
    "isEnabled": true,
    "value": "Reviewer"
  },
  {
    "allowedMemberTypes": ["User", "Application"],
    "description": "Request data access",
    "displayName": "Requester",
    "id": "$(uuidgen)",
    "isEnabled": true,
    "value": "Requester"
  }
]
EOF
)
  
# Path the App Registration to set the App Roles: 
az ad app update --id "$APP1_ID" --set appRoles="$APP_ROLE1"
```

For the Cohort Builder API: 

```bash
APP_ROLE2=$(cat <<EOF
[
  {
    "allowedMemberTypes": ["User", "Application"],
    "description": "Build cohorts",
    "displayName": "Builder",
    "id": "$(uuidgen)",
    "isEnabled": true,
    "value": "Builder"
  },
  {
    "allowedMemberTypes": ["User", "Application"],
    "description": "View cohorts",
    "displayName": "Viewer",
    "id": "$(uuidgen)",
    "isEnabled": true,
    "value": "Viewer"
  }
]
EOF
)

# Path the App Registration to set the App Roles: 
az ad app update --id "$APP2_ID" --set appRoles="$APP_ROLE2"
```

----

## 3. Create platform roles (security groups)

We what a "Platform Adminsitrator and "Platform Researcher" roles. 

```bash 
ADMIN_GROUP_ID=$(az ad group create --display-name "PR_ADMINISTRATOR" --mail-nickname "pr_platform_administrator" --query id -o tsv)
RESEARCHER_GROUP_ID=$(az ad group create --display-name "PR_RESEARCHER" --mail-nickname "pr_platform_researcher" --query id -o tsv)

echo "Platform Admin Group ID: $ADMIN_GROUP_ID"
echo "Platform Researcher Group ID: $RESEARCHER_GROUP_ID"
```

-----

## 4. Assign App Roles to Platform Role security groups 

For the administrator: 

```bash 
# Fetch App Role IDs (we must know which role we're assigning)
APP1_ROLE_ID=$(az ad app show --id "$APP1_ID" --query "appRoles[?value=='Reviewer'].id" -o tsv)
APP2_ROLE_ID=$(az ad app show --id "$APP2_ID" --query "appRoles[?value=='Builder'].id" -o tsv)

# Assign to Platform Admin
az rest --method POST \
  --uri "https://graph.microsoft.com/v1.0/servicePrincipals/$SP1_ID/appRoleAssignedTo" \
  --body "{ \"principalId\": \"$ADMIN_GROUP_ID\", \"resourceId\": \"$SP1_ID\", \"appRoleId\": \"$APP1_ROLE_ID\" }"

az rest --method POST \
  --uri "https://graph.microsoft.com/v1.0/servicePrincipals/$SP2_ID/appRoleAssignedTo" \
  --body "{ \"principalId\": \"$ADMIN_GROUP_ID\", \"resourceId\": \"$SP2_ID\", \"appRoleId\": \"$APP2_ROLE_ID\" }"
```

For the Platform Researcher: 

```bash 
# Now assign different roles to Researcher
APP1_ROLE_ID_2=$(az ad app show --id "$APP1_ID" --query "appRoles[?value=='Requester'].id" -o tsv)
APP2_ROLE_ID_2=$(az ad app show --id "$APP2_ID" --query "appRoles[?value=='Viewer'].id" -o tsv)

az rest --method POST \
  --uri "https://graph.microsoft.com/v1.0/servicePrincipals/$SP1_ID/appRoleAssignedTo" \
  --body "{ \"principalId\": \"$RESEARCHER_GROUP_ID\", \"resourceId\": \"$SP1_ID\", \"appRoleId\": \"$APP1_ROLE_ID_2\" }"

az rest --method POST \
  --uri "https://graph.microsoft.com/v1.0/servicePrincipals/$SP2_ID/appRoleAssignedTo" \
  --body "{ \"principalId\": \"$RESEARCHER_GROUP_ID\", \"resourceId\": \"$SP2_ID\", \"appRoleId\": \"$APP2_ROLE_ID_2\" }"
```

------

