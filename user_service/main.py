from fastapi import FastAPI

from user_service.routes import customers, platform_roles, services, users

app = FastAPI()

app = FastAPI()

app.include_router(services.router, prefix="/services", tags=["Services"])

app.include_router(platform_roles.router, prefix="/platform-roles", tags=["Platform Roles"])

app.include_router(customers.router, prefix="/customers", tags=["Customers"])

app.include_router(users.router, prefix="/users", tags=["Users"])
