from fastapi import APIRouter
from src.org.dtos.OrgCreateRequestDto import OrgCreateRequestDto
from src.org.dtos.OrgCreateResponseDto import OrgCreateResponseDto
from di import OrgServiceDep
from src.org.dtos.OrgSearchResDto import OrgSearchResDto

routes = APIRouter()

@routes.post(
  "/organizations", 
  response_model=OrgCreateResponseDto, 
  tags=["organization"],
  name="act:create-organization"
)
async def createOrganization(
    # 1. Switched to the new Create DTOs
    reqDto: OrgCreateRequestDto,
    orgService: OrgServiceDep
  ) -> OrgCreateResponseDto:
  print("Creating organization with email:", reqDto.email)
  return orgService.createOrg(reqDto)

@routes.get(
  "/organizations/search",
  response_model=list[OrgSearchResDto],
  tags=["organization"],
  name="act:search-organization"
)
async def searchOrganizations(
  q: str, 
  orgService: OrgServiceDep
) -> list[OrgSearchResDto]:
  """
  Autocomplete search for organizations by name.
  Usage: GET /organizations/search?q=Comp
  """
  return orgService.searchOrg(q)