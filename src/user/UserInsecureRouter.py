from fastapi import APIRouter
from di import UserServiceDep
from src.user.dtos.UserRegistrationRequestDto import UserRegistrationRequestDto
from src.user.dtos.UserRegistrationResponseDto import UserRegistrationResponseDto
from src.user.dtos.UserVerificationRequestDto import UserVerificationRequestDto
from src.user.dtos.UserVerificationResponseDto import UserVerificationResponseDto
from src.user.dtos.ForgotPasswordOtpRequestDto import ForgotPasswordOtpRequestDto
from src.user.dtos.ForgotPasswordOtpResponseDto import ForgotPasswordOtpResponseDto
from src.user.dtos.UserJoinOrgRequestDto import UserJoinOrgRequestDto
from src.user.dtos.UserJoinOrgResponseDto import UserJoinOrgResponseDto

routes = APIRouter()

@routes.post(
  "/users/registration", 
  response_model=UserRegistrationResponseDto, 
  tags=["user"]
)
async def registration(
    reqDto: UserRegistrationRequestDto,
    userServiceDep: UserServiceDep
  )->UserRegistrationResponseDto:
  return userServiceDep.registerUser(reqDto)

@routes.post("/users/verify", tags=["user"])
async def verify(
    reqDto: UserVerificationRequestDto, 
    userService: UserServiceDep
  )-> UserVerificationResponseDto:
  return userService.verify(reqDto)

@routes.post("/users/forgot-password-otp", tags=["user"])
async def forgotPassword(
    reqDto: ForgotPasswordOtpRequestDto, 
    userService: UserServiceDep
  )-> ForgotPasswordOtpResponseDto:
  return userService.sendForgotPasswordOtp(reqDto)

@routes.post(
  "/users/join-organization", 
  tags=["user"],
  response_model=UserJoinOrgResponseDto
)
async def joinOrganization(
  reqDto: UserJoinOrgRequestDto,
  userService: UserServiceDep
) -> UserJoinOrgResponseDto:
  """
  Public endpoint for an existing, verified user to request to join an organization.
  The user will be added with 'disabled=True' until an admin approves them.
  """
  return userService.joinOrg(reqDto)