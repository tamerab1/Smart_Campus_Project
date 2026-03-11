from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

# We define the security instance here
security = HTTPBasic()

# This function will be used as a dependency in our routes
def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    # TODO: In the future, check this against the database or a hashed password
    correct_username = "admin"
    correct_password = "123"

    if credentials.username != correct_username or credentials.password != correct_password:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username