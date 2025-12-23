from fastapi import APIRouter
from di import UserServiceDep
from src.user.dtos.UserRegistrationRequestDto import UserRegistrationRequestDto
from src.user.dtos.UserRegistrationResponseDto import UserRegistrationResponseDto
from src.user.dtos.UserVerificationRequestDto import UserVerificationRequestDto
from src.user.dtos.UserVerificationResponseDto import UserVerificationResponseDto
from src.user.dtos.ForgotPasswordOtpRequestDto import ForgotPasswordOtpRequestDto
from src.user.dtos.ForgotPasswordOtpResponseDto import ForgotPasswordOtpResponseDto

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