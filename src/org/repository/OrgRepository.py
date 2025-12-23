from abc import ABC, abstractmethod
from src.org.model.Organization import Organization

class OrgRepository(ABC):

  @abstractmethod
  def getByDomain(self, domain: str) -> Organization:
    pass

  @abstractmethod
  def add(self, org: Organization) -> Organization:
    pass

  @abstractmethod
  def search(self, query: str, limit: int = 10) -> list[Organization]:
    pass

  @abstractmethod
  def getById(self, id: int) -> Organization:
    pass