import jwt
from passlib.context import CryptContext
from src.db.repository.UserOrgLinkRepository import UserOrgLinkRepository
from src.auth.repository.AuthRepository import AuthRepository
from src.auth.dtos.LoginRequestDto import LoginRequestDto
from src.auth.dtos.LoginResponseDto import LoginResponseDto
from src.user.model.User import User
from fastapi import status, HTTPException
from datetime import datetime, timedelta, timezone
from config import Config
from src.auth.dtos.AuthRefreshResponseDto import AuthRefreshResponseDto
from src.auth.dtos.AuthRefreshRequestDto import AuthRefreshRequestDto
from jwt import ExpiredSignatureError
from src.auth.dtos.tokens import Token
from src.db.repository.UserProjectLinkRepository import UserProjectLinkRepository

class AuthService:
  def __init__(
      self, 
      authRepository : AuthRepository, 
      crypto: CryptContext, 
      userOrgLinkRepo: UserOrgLinkRepository,
      userProjectLinkRepo: UserProjectLinkRepository
    ):
    self.repo = authRepository
    self.crypto = crypto
    self.userOrgLinkRepo = userOrgLinkRepo
    self.userProjectLinkRepo = userProjectLinkRepo

  def login(self, reqDto: LoginRequestDto) -> LoginResponseDto: # Updated return type hint
    dbUser: User = self.repo.getUserByEmail(reqDto.email)

    if not dbUser:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user found by this email!")
    
    if not dbUser.verified:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not verified yet!")
  
    isPasswordVerified = self.crypto.verify(reqDto.password, dbUser.password)

    if not isPasswordVerified:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password!")
    
    # --- NEW NESTED LOGIC START ---
    activeOrgsWithProjects = []

    for org in dbUser.orgs:
      # 1. Check if User is active in this Org
      orgLink = self.userOrgLinkRepo.get(dbUser.id, org.id)
      if not orgLink or orgLink.disabled:
        continue

      # 2. Find valid projects for this specific Org
      orgProjects = []
      for project in dbUser.projects:
        # Only check projects belonging to the current loop's organization
        if project.orgId == org.id:
          projLink = self.userProjectLinkRepo.get(dbUser.id, project.id)
          
          if projLink and not projLink.disabled:
            orgProjects.append({
              "id": project.id,
              "name": project.name
            })
      
      # 3. Build the nested structure
      activeOrgsWithProjects.append({
        "id": org.id,
        "name": org.name,
        "projects": orgProjects
      })
    
    # --- NEW NESTED LOGIC END ---

    if not activeOrgsWithProjects:
      raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, 
        detail="Your account is disabled in all organizations!"
      )

    # Note: We now pass the nested list. We no longer need a separate 'projects' argument.
    token = self.generateToken(dbUser, activeOrgsWithProjects)

    res = LoginResponseDto(accessToken=token.accessToken, refreshToken=token.refreshToken)
    return res
  
  def refresh(self, authRefreshRequestDto: AuthRefreshRequestDto)-> AuthRefreshResponseDto:
    refreshToken = authRefreshRequestDto.refreshToken

    try:
      payload = jwt.decode(refreshToken, Config.getValByKey("SECRET_KEY"), Config.getValByKey("ALGORITHM"))
    except ExpiredSignatureError as e:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired!")

    payloadEmail = payload.get("sub")

    if payloadEmail is None:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No email found on token payload!")
    
    dbUser: User = self.repo.getUserByEmail(payloadEmail)

    if not dbUser:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user found by this email!")
    
    token = self.generateToken(dbUser)

    res  = AuthRefreshResponseDto(accessToken=token.accessToken,refreshToken=token.refreshToken)
    return res
  
  def generateToken(self, user: User, orgs : list)->Token:
    accessTokenExpires = datetime.now(timezone.utc) + timedelta(minutes=int(Config.getValByKey("ACCESS_TOKEN_EXPIRE_MINUTES")))
    refreshTokenExpires = datetime.now(timezone.utc) + timedelta(minutes=int(Config.getValByKey("REFRESH_TOKEN_EXPIRE_MINUTES")))

    accessToken = jwt.encode({
      "sub" : user.email,
      "userId": user.id,
      "orgs" : orgs,
      "exp" : accessTokenExpires
    }, Config.getValByKey("SECRET_KEY"), Config.getValByKey("ALGORITHM"))

    refreshToken = jwt.encode({
      "sub" : user.email,
      "userId": user.id,
      "orgs" : orgs,
      "exp" : refreshTokenExpires
    }, Config.getValByKey("SECRET_KEY"), Config.getValByKey("ALGORITHM"))
    
    return Token(accessToken=accessToken,refreshToken=refreshToken)

  
