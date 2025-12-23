import random
from config import Config
from src.user.model.User import User
from datetime import datetime, timezone
from passlib.context import CryptContext
from fastapi import status, HTTPException
from src.org.dtos.OrgAddReqDto import OrgAddReqDto
from src.org.dtos.OrgAddResDto import OrgAddResDto
from src.user.dtos.UserRegistrationRequestDto import UserRegistrationRequestDto
from src.user.dtos.UserRegistrationResponseDto import UserRegistrationResponseDto
from src.user.repository.UserRepository import UserRepository
from src.user.dtos.UserResponseDto import UserResponseDto
from src.user.dtos.UserVerificationRequestDto import UserVerificationRequestDto
from src.user.dtos.UserVerificationResponseDto import UserVerificationResponseDto
from src.email.EmailService import EmailService
from src.user.dtos.ForgotPasswordOtpRequestDto import ForgotPasswordOtpRequestDto
from src.user.dtos.ForgotPasswordOtpResponseDto import ForgotPasswordOtpResponseDto
from src.org.model.Organization import Organization
from src.org.repository.OrgRepository import OrgRepository
from src.user.dtos.UpdateUserRequestDto import UpdateUserRequestDto
from src.user.dtos.UpdateUserResponseDto import UpdateUserResponseDto
from src.db.repository.UserOrgLinkRepository import UserOrgLinkRepository
from src.db.links.UserOrgLink import UserOrgLink
from src.utils.pagination.PaginationRequestDto import PaginationRequestDto
from src.utils.pagination.PaginationResponseDto import PaginationResponseDto
from src.utils.Constants import OTP_POPULATION_DIGITS, USER_CREATION_RES_MSG

class UserService:
  otpExpiryDuration: int = int(Config.getValByKey("OTP_EXPIRY_DURATION"))

  def __init__(
    self, 
    userRepository : UserRepository, 
    orgRepository: OrgRepository,
    userOrgLinkRepo: UserOrgLinkRepository,
    crypto: CryptContext,
    emailService : EmailService
  ):
    self.repo = userRepository
    self.crypto = crypto
    self.emailService = emailService
    self.orgRepo = orgRepository
    self.userOrgLinkRepo = userOrgLinkRepo

  def registerUser(self, reqDto : UserRegistrationRequestDto) -> UserRegistrationResponseDto:
    org = self.orgRepo.getById(reqDto.orgId)
    
    otp = self.generateOtp()
    truncatedPassword = reqDto.password[:72]
    
    # Note: UserOrgLink will be created automatically with default values (disabled=True)
    newUser = self.repo.add(User(
      email=reqDto.email,
      password=self.crypto.hash(truncatedPassword),
      otp=otp,
      orgs=[org],         
      menuTemplates=[] 
    ))

    self.emailService.sendAccountVerificationOtp(newUser.email, otp)

    resUser = UserRegistrationResponseDto(
      id=newUser.id,
      email=newUser.email,
      message=USER_CREATION_RES_MSG
    )

    return resUser
  
  def getUserById(self, id: int)-> UserResponseDto:
    dbUser = self.repo.getUserById(id=id)
    return UserResponseDto(
      id=dbUser.id, 
      email=dbUser.email,
      contactNumber=dbUser.contactNumber,
      firstName=dbUser.firstName,
      lastName=dbUser.lastName,
      verified=dbUser.verified
    )
  
  def generateOtp(self)->str:
    otp = ''.join(random.choices(OTP_POPULATION_DIGITS, k=6))
    return otp
  
  def verify(self, reqDto: UserVerificationRequestDto)-> UserVerificationResponseDto:

    dbUser: User = self.repo.getUserByEmail(reqDto.email)

    if not dbUser:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user found by this email!")
    
    if dbUser.verified:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already verified!")
    
    if not dbUser.createdAt:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No otp creation date found to calculate otp expiration!")

    otpDuration: int = self.calculateSecondDiff(datetime.now(timezone.utc), dbUser.createdAt)

    if otpDuration > self.otpExpiryDuration :
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Otp expired!")

    if dbUser.otp != reqDto.otp:
      raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Otp didn't match!")
    
    dbUser.verified = True

    self.repo.updateUser(dbUser)

    resDto = UserVerificationResponseDto(message="User verified successfully!")
    return resDto
  
  def sendForgotPasswordOtp(
      self, 
      reqDto: ForgotPasswordOtpRequestDto
    ) -> ForgotPasswordOtpResponseDto :
    
    dbUser: User = self.repo.getUserByEmail(reqDto.email)

    if not dbUser:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user found by this email!")
    
    otp = self.generateOtp()
    dbUser.otp = otp
    self.repo.updateUser(dbUser)

    self.emailService.sendForgotPasswordOtp(dbUser.email, otp)

    return ForgotPasswordOtpResponseDto(message="To reset your password, a otp has been sent to your mail!")
  
  def calculateSecondDiff(self, end: datetime, start: datetime) -> int:
    timeDiff = end - start
    return timeDiff.seconds

  # 1. Update logic to use the strict fields from OrgAddReqDto
  def addOrg(self, reqDto: OrgAddReqDto, authMail: str) -> OrgAddResDto: 
    adminUser: User = self.repo.getUserByEmail(authMail)
    if not adminUser:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin user not found!")

    targetUser: User = self.repo.getUserByEmail(reqDto.email)
    if not targetUser:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User to add not found!")

    # 2. Domain is now mandatory in the DTO, so we use it directly
    org = self.orgRepo.getByDomain(reqDto.domain)

    if not org:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found!")

    existingLink = self.userOrgLinkRepo.get(userId=targetUser.id, orgId=org.id)
    if existingLink:
      raise HTTPException(status_code=status.HTTP_302_FOUND, detail="User is already in this organization!")
    
    newLink = UserOrgLink(
      userId=targetUser.id,
      orgId=org.id,
      roleId=reqDto.roleId,
      menuTemplateId=reqDto.menuTemplateId,
      disabled=False,
      super=False
    )
    
    self.userOrgLinkRepo.add(newLink)

    return OrgAddResDto(id=org.id, name=org.name, email=org.email)

  def updateUser(self, userId: int, orgId: int, reqDto: UpdateUserRequestDto)-> UpdateUserResponseDto:
    dbUser: User = self.repo.getUserById(userId)

    if not dbUser:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user found by this ID!")
    
    if reqDto.firstName:
      dbUser.firstName = reqDto.firstName

    if reqDto.lastName:
     dbUser.lastName = reqDto.lastName

    if reqDto.contactNumber:
      dbUser.contactNumber = reqDto.contactNumber

    updateUser = self.repo.updateUser(dbUser)

    userOrgLink: UserOrgLink|None = self.userOrgLinkRepo.get(userId=userId,orgId=orgId)

    if userOrgLink is not None:
      if reqDto.disabled is not None:
        userOrgLink.disabled = reqDto.disabled

      if reqDto.super is not None:
        userOrgLink.super = reqDto.super
      
      if reqDto.roleId is not None:
        userOrgLink.roleId = reqDto.roleId
        
      if reqDto.menuTemplateId is not None:
        userOrgLink.menuTemplateId = reqDto.menuTemplateId

      self.userOrgLinkRepo.edit(userOrgLink=userOrgLink)

    return UpdateUserResponseDto(
      id=updateUser.id, 
      disabled= None if userOrgLink is None else userOrgLink.disabled,
      super= None if userOrgLink is None else userOrgLink.super,
      firstName=updateUser.firstName,
      lastName=updateUser.lastName,
      contactNumber=updateUser.contactNumber
    )
  
  def getUsers(self, reqDto: PaginationRequestDto)->PaginationResponseDto[UserResponseDto]:
    total: int|None = reqDto.total
    userResponseDtoList: list[UserResponseDto] = []
    
    users: list[User] = self.repo.getAllUser(rows=reqDto.rows, page=reqDto.page, orgId=reqDto.orgId)

    if reqDto.total is None or reqDto.total == 0:
      total = self.repo.countAllUser(orgId=reqDto.orgId)

    for u,l in users:
      urDto: UserResponseDto = UserResponseDto(
        id=u.id,
        email=u.email,
        contactNumber=u.contactNumber,
        firstName=u.firstName,
        lastName=u.lastName,
        verified=u.verified,
        super=l.super,
        disabled=l.disabled
      )

      userResponseDtoList.append(urDto)

    return PaginationResponseDto[UserResponseDto](items=userResponseDtoList, total=total)