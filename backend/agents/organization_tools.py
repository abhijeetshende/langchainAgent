import os
import uuid
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, String, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

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

    name = Column(String, primary_key=True)  # Using org_name as primary key
    org_type = Column(Enum(*ORG_TYPES, name="org_type_enum"), nullable=False)
    super_admin_email = Column(String, nullable=False)
    status = Column(String, nullable=True)  # ACTIVE, CREATED, INACTIVE
    reg_address = Column(String, nullable=True)
    description = Column(String, nullable=True)

Base.metadata.create_all(bind=engine)  # Ensure table creation



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
        )
        session.add(org)
        session.commit()
        return f"Organization '{name}' created with ID {org.id}."
    
    except Exception as e:
        return f"Error creating organization: {str(e)}"
    
    finally:
        session.close()


def fetch_organizations(input_str: str = "", *args, **kwargs):
    """
    Fetch all organizations.
    Accepts an optional empty input.
    """
    session = SessionLocal()
    try:
        orgs = session.query(Organization).all()
        if not orgs:
            return "No organizations found."

        return "\n".join([f"{org.name}|{org.org_type}" for org in orgs])
    
    finally:
        session.close()


def update_organization_address(input_str: str, *args, **kwargs):
    """
    Updates the address of an organization.
    Expected input format: "update address of <org_name> to <new_address>"
    """
    session = None
    try:
        parts = input_str.split(" to ")
        if len(parts) != 2:
            return "Invalid input format. Use: update address of <org_name> to <new_address>"

        org_name = parts[0].replace("update address of", "").strip()
        new_address = parts[1].strip()

        session = SessionLocal()
        org = session.query(Organization).filter(Organization.name == org_name).first()

        if not org:
            return f"Organization '{org_name}' not found."

        org.reg_address = new_address
        session.commit()
        return f"Updated address of '{org_name}' to '{new_address}'."
    
    except Exception as e:
        return f"Error updating address: {str(e)}"
    
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
