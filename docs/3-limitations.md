# Limitations of this approach: 

## Maximum number of role-assignable groups 

> A maximum of 500 role-assignable groups can be created in a single Microsoft Entra organization (tenant).

Reference: https://learn.microsoft.com/en-us/entra/identity/users/directory-service-limits-restrictions

Keep in mind: each TRE workspace will also create 3 groups. 

**Example calculation**: 

| Component              | Count   | Groups per Item   | Total Groups    |
|------------------------|---------|-------------------|-----------------|
| TRE Workspaces         | 150     | 3                 | 450             |
| Customer Organizations | 20      | 1                 | 20              | 
| Platform Roles         | 5       | 1                 | 5               |
| **Total**                  |         |                   | **475**         |


This leaves little headroom under the 500-group limit.

---

## Entra quotas / limits 

| Metric             | Limit                                                     |
|--------------------|-----------------------------------------------------------|
| Per app per tenant | ~ 10 requests per second (soft throttle)                  | 
| Burst tolerance    | Small bursts OK, but sustained >10 rps will result in 429 |


Azure will respond with HTTP 429 Too Many Requests if you exceed the limit. It may also include a Retry-After header.

Reference https://learn.microsoft.com/en-us/entra/identity/users/directory-service-limits-restrictions


---

## Graph API quotas 

| Request type	  | Limit per app per tenant 	         | Limit per tenant for all apps     |
|----------------|------------------------------------|-----------------------------------|
| Any            | 500 requests per 10 seconds        | 1,000 requests per 10 seconds     |
| Any	           | 15,000 requests per 3,600 seconds	 | 30,000 requests per 3,600 seconds | 

Reference https://learn.microsoft.com/en-us/graph/throttling-limits
