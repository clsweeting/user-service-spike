#!/bin/bash

set -e

# === Config ===
APP1_NAME="Data Access Requests API"
APP2_NAME="Cohort Builder API"

# === 1. Create App Registrations ===

APP1_ID=$(az ad app create --display-name "$APP1_NAME" --query appId -o tsv 2>/dev/null || az ad app list --display-name "$APP1_NAME" --query "[0].appId" -o tsv)
APP2_ID=$(az ad app create --display-name "$APP2_NAME" --query appId -o tsv 2>/dev/null || az ad app list --display-name "$APP2_NAME" --query "[0].appId" -o tsv)

# === 2. Create (or get) Service Principals ===
SP1_ID=$(az ad sp list --filter "appId eq '$APP1_ID'" --query "[0].id" -o tsv)
if [ -z "$SP1_ID" ]; then
  SP1_ID=$(az ad sp create --id "$APP1_ID" --query id -o tsv)
fi

SP2_ID=$(az ad sp list --filter "appId eq '$APP2_ID'" --query "[0].id" -o tsv)
if [ -z "$SP2_ID" ]; then
  SP2_ID=$(az ad sp create --id "$APP2_ID" --query id -o tsv)
fi

# === 3. Define App Roles ===
APP_ROLE1=$(uuidgen)
APP_ROLE2=$(uuidgen)
APP_ROLE3=$(uuidgen)
APP_ROLE4=$(uuidgen)

APP1_ROLES_JSON="[
  {
    \"allowedMemberTypes\": [\"User\"],
    \"description\": \"Review data access requests\",
    \"displayName\": \"Reviewer\",
    \"id\": \"$APP_ROLE1\",
    \"isEnabled\": true,
    \"value\": \"Reviewer\"
  },
  {
    \"allowedMemberTypes\": [\"User\"],
    \"description\": \"Request data access\",
    \"displayName\": \"Requester\",
    \"id\": \"$APP_ROLE2\",
    \"isEnabled\": true,
    \"value\": \"Requester\"
  }
]"

APP2_ROLES_JSON="[
  {
    \"allowedMemberTypes\": [\"User\"],
    \"description\": \"Build cohorts\",
    \"displayName\": \"Builder\",
    \"id\": \"$APP_ROLE3\",
    \"isEnabled\": true,
    \"value\": \"Builder\"
  },
  {
    \"allowedMemberTypes\": [\"User\"],
    \"description\": \"View cohorts\",
    \"displayName\": \"Viewer\",
    \"id\": \"$APP_ROLE4\",
    \"isEnabled\": true,
    \"value\": \"Viewer\"
  }
]"

az ad app update --id "$APP1_ID" --set appRoles="$APP1_ROLES_JSON"
az ad app update --id "$APP2_ID" --set appRoles="$APP2_ROLES_JSON"

# === 4. Create Platform Role Groups ===
ADMIN_GROUP_ID=$(az ad group create --display-name "PR_ADMINISTRATOR" --mail-nickname "pr_administrator" --query id -o tsv)
RESEARCHER_GROUP_ID=$(az ad group create --display-name "PR_RESEARCHER" --mail-nickname "pr_researcher" --query id -o tsv)

# === 5. Assign Roles to Groups ===
# Platform Admin gets Reviewer + Builder
az rest --method POST \
  --uri "https://graph.microsoft.com/v1.0/servicePrincipals/$SP1_ID/appRoleAssignedTo" \
  --body "{ \"principalId\": \"$ADMIN_GROUP_ID\", \"resourceId\": \"$SP1_ID\", \"appRoleId\": \"$APP_ROLE1\" }"

az rest --method POST \
  --uri "https://graph.microsoft.com/v1.0/servicePrincipals/$SP2_ID/appRoleAssignedTo" \
  --body "{ \"principalId\": \"$ADMIN_GROUP_ID\", \"resourceId\": \"$SP2_ID\", \"appRoleId\": \"$APP_ROLE3\" }"

# Platform Researcher gets Requester + Viewer
az rest --method POST \
  --uri "https://graph.microsoft.com/v1.0/servicePrincipals/$SP1_ID/appRoleAssignedTo" \
  --body "{ \"principalId\": \"$RESEARCHER_GROUP_ID\", \"resourceId\": \"$SP1_ID\", \"appRoleId\": \"$APP_ROLE2\" }"

az rest --method POST \
  --uri "https://graph.microsoft.com/v1.0/servicePrincipals/$SP2_ID/appRoleAssignedTo" \
  --body "{ \"principalId\": \"$RESEARCHER_GROUP_ID\", \"resourceId\": \"$SP2_ID\", \"appRoleId\": \"$APP_ROLE4\" }"


echo "Setup complete."
echo "Platform Admin Group ID: $ADMIN_GROUP_ID"
echo "Platform Researcher Group ID: $RESEARCHER_GROUP_ID"

