import os
import uuid
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://abhijeet:abhi123@postgres:5432/mydatabase")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Site(Base):
    __tablename__ = "sites"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True)
    street_address = Column(String, nullable=True)
    org_name = Column(String, nullable=False)  # No ForeignKey, will be manually resolved

# Ensure `organizations` exist before creating `sites`
def init_db():
    """Ensures tables are created in the correct order"""
    from agents.organization_tools import Base as OrgBase
    OrgBase.metadata.create_all(bind=engine)  # Ensure organizations are created first
    Base.metadata.create_all(bind=engine)  # Then create sites

init_db()  # Call when module loads




from agents.organization_tools import Organization

def create_site(input_str: str, *args, **kwargs):
    """
    Creates a site linked to an organization by name.
    Expected input format: org_name|name|description|street_address
    """
    try:
        parts = input_str.split("|")
        if len(parts) < 2:
            return "Invalid format. Use: org_name|name|description|street_address"
        
        org_name = parts[0].strip()
        name = parts[1].strip()
        description = parts[2].strip() if len(parts) > 2 else None
        street_address = parts[3].strip() if len(parts) > 3 else None

        session = SessionLocal()
        org = session.query(Organization).filter(Organization.name.ilike(org_name)).first()
        
        if not org:
            return f"Organization with name '{org_name}' not found."

        site = Site(
            name=name,
            description=description,
            street_address=street_address,
            org_name=org.name  # Store organization name
        )
        session.add(site)
        session.commit()
        return f"Site '{name}' created under Organization '{org.name}'."
    
    except Exception as e:
        return f"Error creating site: {str(e)}"
    
    finally:
        session.close()

def fetch_sites(input_str: str = "", *args, **kwargs):
    """
    Fetch all sites.
    Accepts an optional empty input.
    """
    session = SessionLocal()
    try:
        sites = session.query(Site).all()
        if not sites:
            return "No sites found."

        return "\n".join([f"{site.name}|{site.street_address}" for site in sites])
    
    finally:
        session.close()


def fetch_sites_by_org(org_name: str, *args, **kwargs):
    """
    Fetch all sites under a specific organization by its name.
    """
    session = SessionLocal()
    try:
        sites = session.query(Site).filter(Site.org_name.ilike(org_name.strip())).all()
        
        if not sites:
            return f"No sites found for Organization '{org_name}'."

        return "\n".join([f"{site.id}|{site.name}|{site.street_address}" for site in sites])
    
    finally:
        session.close()


def update_site(input_str: str, *args, **kwargs):
    """
    Updates a site.
    Expected input format: site_id|name|description|street_address
    """
    session = None
    try:
        parts = input_str.split("|")
        if len(parts) < 2:
            return "Invalid format. Use: site_id|name|description|street_address"
        
        site_id, name = parts[0].strip(), parts[1].strip()
        description = parts[2].strip() if len(parts) > 2 else None
        street_address = parts[3].strip() if len(parts) > 3 else None

        session = SessionLocal()
        site = session.query(Site).filter(Site.id == site_id).first()
        
        if not site:
            return f"Site with ID {site_id} not found."

        site.name = name
        site.description = description
        site.street_address = street_address

        session.commit()
        return f"Site '{site.name}' updated."
    
    except Exception as e:
        return f"Error updating site: {str(e)}"
    
    finally:
        if session:
            session.close()


def delete_site(input_str: str, *args, **kwargs):
    """
    Deletes a site by name.
    Expected input: site_name
    """
    session = None
    try:
        site_name = input_str.strip()

        session = SessionLocal()
        site = session.query(Site).filter(Site.name == site_name).first()
        
        if not site:
            return f"Site with name '{site_name}' not found."

        session.delete(site)
        session.commit()
        return f"Site '{site.name}' deleted."
    
    except Exception as e:
        return f"Error deleting site: {str(e)}"
    
    finally:
        if session:
            session.close()
