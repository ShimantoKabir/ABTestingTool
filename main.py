from fastapi import Depends, Header
from src.user import UserRouter
from src.user import UserInsecureRouter
from src.menu import MenuRouter
from src.auth import AuthRouter
from src.role import RoleRouter
from src.menutemplate import MenuTemplateRouter
from src.auth.AuthMiddleware import AuthMiddleware
from fastapi.security import HTTPBearer
from typing import Annotated
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from src.action import ActionRouter
from src.project import ProjectRouter
from src.org import OrgRouter
from src.experiment import ExperimentRouter 
from src.variation import VariationRouter
from src.condition import ConditionRouter
from src.metrics import MetricsRouter
from src.metrics import MetricsInsecureRouter
from src.decision import DecisionRouter
from core import app

# IMPORT Models
from src.user.model.User import User
from src.org.model.Organization import Organization
from src.menu.model.Menu import Menu
from src.role.model.Role import Role
from src.menutemplate.model.MenuTemplate import MenuTemplate
from src.experiment.model.Experiment import Experiment
from src.variation.model.Variation import Variation
from src.condition.model.Condition import Condition
from src.metrics.model.Metrics import Metrics
from src.bucket.model.Bucket import Bucket
from src.db.links.UserOrgLink import UserOrgLink
from src.db.links.UserProjectLink import UserProjectLink
from src.project.model.Project import Project

def getEmail(email: Annotated[str, Header()]):
  return email

app.include_router(UserRouter.routes, dependencies=[Depends(getEmail), Depends(HTTPBearer())])
app.include_router(MenuRouter.routes, dependencies=[Depends(getEmail), Depends(HTTPBearer())])
app.include_router(RoleRouter.routes, dependencies=[Depends(getEmail), Depends(HTTPBearer())])
app.include_router(MenuTemplateRouter.routes, dependencies=[Depends(getEmail), Depends(HTTPBearer())])
app.include_router(ActionRouter.routes, dependencies=[Depends(getEmail), Depends(HTTPBearer())])
app.include_router(ProjectRouter.routes, dependencies=[Depends(getEmail), Depends(HTTPBearer())])
app.include_router(ExperimentRouter.routes, dependencies=[Depends(getEmail), Depends(HTTPBearer())])
app.include_router(VariationRouter.routes, dependencies=[Depends(getEmail), Depends(HTTPBearer())])
app.include_router(ConditionRouter.routes, dependencies=[Depends(getEmail), Depends(HTTPBearer())])
app.include_router(MetricsRouter.routes, dependencies=[Depends(getEmail), Depends(HTTPBearer())])
app.include_router(MetricsInsecureRouter.routes)
app.include_router(DecisionRouter.routes)
app.include_router(AuthRouter.routes)
app.include_router(UserInsecureRouter.routes)
app.include_router(OrgRouter.routes)

app.add_middleware(AuthMiddleware)

origins = [
  "http://localhost:3000",  
  "http://127.0.0.1:3000",
  "http://localhost:3030"
]

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,             
  allow_credentials=True,            
  allow_methods=["*"],        
  allow_headers=["*"],               
)

app.mount("/static", StaticFiles(directory="static"), name="static")