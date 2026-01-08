import jwt
import re
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response, status
from config import Config
from jwt import ExpiredSignatureError

class AuthMiddleware(BaseHTTPMiddleware):

  def __init__(self, app):
    super().__init__(app)

  async def dispatch(self, request: Request, call_next)-> Response:
    excludedPaths = [
      "/docs",
      "/openapi.json",
      "/auth/login", 
      "/", 
      "/auth/refresh", 
      "/users/registration",
      "/users/verify",
      "/users/forgot-password-otp",
      "/users/join-organization",
      "/static/menu.json",
      "/organizations",
      "/organizations/search",
      "/static/client-sdk.js",
      "/decision",
      "/metrics/track"
    ]

    excludedRegexs = []

    if request.url.path in excludedPaths:
      return await call_next(request)
    
    for pattern in excludedRegexs:
      if re.match(pattern, request.url.path):
        return await call_next(request)

    authorization = request.headers.get("authorization")
    authEmail = request.headers.get("email")
    
    if not authEmail:
      return Response(content="No mail found on header!",status_code=status.HTTP_403_FORBIDDEN)

    if not authorization:
      return Response(content="No authorization found!",status_code=status.HTTP_403_FORBIDDEN)

    token = authorization.split(" ")[1].strip()
    response = await self.verifyToken(token=token, authEmail=authEmail)

    if response:
      return response

    return await call_next(request)
  
  async def verifyToken(self, token: str, authEmail: str):
    try:
      payload = jwt.decode(token, Config.getValByKey("SECRET_KEY"), Config.getValByKey("ALGORITHM"))
    except ExpiredSignatureError as e:
      return Response(content="Token expired!",status_code=status.HTTP_401_UNAUTHORIZED)
    
    payloadEmail = payload.get("sub")

    if payloadEmail is None:
      return Response(content="No email found on token payload!",status_code=status.HTTP_401_UNAUTHORIZED)

    if authEmail != payloadEmail:
      raise Response(content="Auth token email didn't match with header token!", status_code=status.HTTP_404_NOT_FOUND)
    

    