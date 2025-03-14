from sqlalchemy import create_engine, Column, String, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

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

    name = Column(String, primary_key=True)  # Name as primary key
    org_type = Column(Enum(*ORG_TYPES, name="org_type_enum"), nullable=True)
    super_admin_email = Column(String, nullable=True)
    status = Column(String, nullable=True)  # ACTIVE, CREATED, INACTIVE
    reg_address = Column(String, nullable=True)
    description = Column(String, nullable=True)

Base.metadata.create_all(bind=engine)  # Ensure table creation



def create_organization(input_str: str, *args, **kwargs):
    """
    Creates an organization with just a name.
    Expected input format: name
    """
    session = SessionLocal()
    try:
        name = input_str.strip()
        if not name:
            return "Invalid input: Organization name cannot be empty."

        existing_org = session.query(Organization).filter(Organization.name == name).first()
        if existing_org:
            return f"Organization '{name}' already exists."

        org = Organization(name=name)
        session.add(org)
        session.commit()
        return f"Organization '{name}' created successfully."

    except Exception as e:
        return f"Error creating organization: {str(e)}"

    finally:
        session.close()

def fetch_organizations(input_str: str = "", *args, **kwargs):
    """
    Fetch all organizations.
    """
    session = SessionLocal()
    try:
        orgs = session.query(Organization).all()
        if not orgs:
            return "No organizations found."

        return "\n".join([f"{org.name} | {org.org_type or 'N/A'} | {org.status or 'N/A'}" for org in orgs])

    finally:
        session.close()

def update_organization(input_str: str, *args, **kwargs):
    """
    Updates an organization's details.
    Expected input format: name|[org_type]|[super_admin_email]|[status]|[reg_address]|[description]
    Fields in brackets [] are optional.
    """
    session = SessionLocal()
    try:
        parts = input_str.split("|")
        name = parts[0].strip() if parts else ""

        if not name:
            return "Invalid input: Organization name is required."

        org = session.query(Organization).filter(Organization.name == name).first()
        if not org:
            return f"Organization '{name}' not found."

        # Define updatable fields and map them to the input
        field_names = ["org_type", "super_admin_email", "status", "reg_address", "description"]
        updates = {field_names[i]: parts[i + 1].strip() for i in range(len(parts) - 1) if parts[i + 1].strip()}

        # Apply updates dynamically
        for field, value in updates.items():
            setattr(org, field, value)

        session.commit()
        return f"Organization '{name}' updated successfully with changes: {updates}"

    except Exception as e:
        return f"Error updating organization: {str(e)}"

    finally:
        session.close()


import uuid

def delete_organization(input_str: str, *args, **kwargs):
    """
    Deletes an organization by name.
    Expected input format: name
    """
    session = SessionLocal()
    try:
        name = input_str.strip()
        if not name:
            return "Invalid input: Organization name cannot be empty."

        org = session.query(Organization).filter(Organization.name == name).first()
        if not org:
            return f"Organization '{name}' not found."

        session.delete(org)
        session.commit()
        return f"Organization '{name}' deleted successfully."

    except Exception as e:
        return f"Error deleting organization: {str(e)}"

    finally:
        session.close()
