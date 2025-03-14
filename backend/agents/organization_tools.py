import os
import datetime
import uuid
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, String, Enum, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://abhijeet:abhi123@postgres:5432/mydatabase")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define valid organization types
ORG_TYPES = ("PARTNER", "CUSTOMER", "RAMEN")

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, index=True)
    org_type = Column(Enum(*ORG_TYPES, name="org_type_enum"), nullable=False)
    super_admin_email = Column(String, nullable=False)
    status = Column(String, nullable=True)  # ACTIVE, CREATED, INACTIVE
    reg_address = Column(String, nullable=True)
    description = Column(String, nullable=True)
    logo_id = Column(String, nullable=True)
    org_stats = Column(JSON, nullable=True)
    hierarchy = Column(JSON, nullable=True)  # For nested structures

Base.metadata.create_all(bind=engine)



def create_organization(input_str: str, *args, **kwargs):
    """
    Creates an organization.
    Expected input format: name|org_type|super_admin_email|status|reg_address|description
    """
    try:
        parts = input_str.split("|")
        if len(parts) != 6:
            return "Invalid input format. Use: name|org_type|super_admin_email|status|reg_address|description"
        
        name, org_type, super_admin_email, status, reg_address, description = parts
        session = SessionLocal()
        
        org = Organization(
            name=name.strip(),
            org_type=org_type.strip(),
            super_admin_email=super_admin_email.strip(),
            status=status.strip(),
            reg_address=reg_address.strip() if reg_address else None,
            description=description.strip() if description else None,
            org_stats={},  # Empty stats initially
            hierarchy=[],  # Empty hierarchy initially
        )
        session.add(org)
        session.commit()
        return f"Organization '{name}' created with ID {org.id}."
    
    except Exception as e:
        return f"Error creating organization: {str(e)}"
    
    finally:
        session.close()


def fetch_organizations(*args, **kwargs):
    """
    Fetch all organizations in a hierarchical structure.
    Returns a newline-separated list of organization IDs and names.
    """
    session = SessionLocal()
    try:
        orgs = session.query(Organization).all()
        if not orgs:
            return "No organizations found."

        # Return IDs in a simple, parseable format
        return "\n".join([f"{org.id}|{org.name}" for org in orgs])
    
    finally:
        session.close()


def update_organization(input_str: str, *args, **kwargs):
    """
    Updates an organization.
    Expected input format: id|name|org_type|super_admin_email|status|reg_address|description
    """
    session = None
    try:
        parts = input_str.split("|")
        if len(parts) != 7:
            return "Invalid input format. Use: id|name|org_type|super_admin_email|status|reg_address|description"
        
        org_id, name, org_type, super_admin_email, status, reg_address, description = parts
        session = SessionLocal()
        org = session.query(Organization).filter(Organization.id == uuid.UUID(org_id.strip())).first()
        
        if not org:
            return f"Organization with ID {org_id} not found."
        
        org.name = name.strip()
        org.org_type = org_type.strip()
        org.super_admin_email = super_admin_email.strip()
        org.status = status.strip()
        org.reg_address = reg_address.strip() if reg_address else None
        org.description = description.strip() if description else None
        
        session.commit()
        return f"Organization '{org.name}' updated."
    
    except Exception as e:
        return f"Error updating organization: {str(e)}"
    
    finally:
        if session:
            session.close()


import uuid

def delete_organization(input_str: str, *args, **kwargs):
    """
    Deletes an organization by ID.
    Expects input format: org_id
    """
    session = None
    try:
        org_id = input_str.strip()
        
        # Validate UUID format
        try:
            uuid_obj = uuid.UUID(org_id)
        except ValueError:
            return f"Invalid UUID format: {org_id}"

        session = SessionLocal()
        org = session.query(Organization).filter(Organization.id == uuid_obj).first()
        
        if not org:
            return f"Organization with ID {org_id} not found."
        
        session.delete(org)
        session.commit()
        return f"Organization with ID {org_id} deleted successfully."
    
    except Exception as e:
        return f"Error deleting organization: {str(e)}"
    
    finally:
        if session:
            session.close()
