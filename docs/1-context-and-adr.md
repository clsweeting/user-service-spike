## Context

We are building an **admin portal** (also referred to as the “control center”) where administrators can manage user access.

Rather than assigning multiple low-level service roles to each user individually, we want to group them into **Platform Roles** — logical role bundles that can be assigned in one step.

Initially, we’ve defined two platform roles:

- `Platform Administrator`
- `Platform Researcher`

Additional platform roles may be introduced later.

We also need a way to represent **customer organizations** (e.g., AstraZeneca, Roche, NHS) in the identity model — i.e., to tag or scope users by their organizational context.

Other considerations: 
- This service is MAINLY for administrative purposes - for the control center. 
- It is not a high usage service.  
- The APIs are not hit when end users access the actual services. 
- It's assumed that users are NOT onboarded via these APIs. (but rather via inviation to Entra ID)


---

## Considered Options

We evaluated two main architectural approaches:

1. **Custom Metadata Store**: Use Cosmos DB to track platform roles, mappings, and user-role assignments. Synchronize these to Azure AD.
2. **Azure-native Approach**: Use **Azure Entra Security Groups** to represent platform roles and customer organizations directly.

---

## Decision Drivers

1. **Security** — Aligning access control with Entra ID’s boundary and enforcement
2. **Simplicity & Maintainability** — Minimize moving parts and operational complexity
3. **Scalability** — Avoid custom sync infrastructure and eventual consistency issues

---

## Decision

We chose to use **Azure Entra Security Groups** for both platform roles and customer groups.

### Benefits

- ✅ **Security boundary alignment** — group membership is evaluated directly by Entra ID
- ✅ **Operational simplicity** — no need for a sync layer or duplicate data store
- ✅ **Auditability and traceability** — changes to group membership are natively logged by Entra

### Rejected: Cosmos DB + Sync Layer

- ❌ **Extra operational burden** — sync code, retries, schema validation, versioning
- ❌ **Risk of drift** — deleted or stale roles may conflict between the two systems  
- ❌ **Higher complexity** — multiple sources of truth for identity and roles