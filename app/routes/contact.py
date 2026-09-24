from datetime import datetime, timezone
from uuid import uuid4
from fastapi import APIRouter
from pydantic import BaseModel, EmailStr, Field, field_validator
from app.database.cosmos import save_contact
from app.services.email import send_contact_email

router = APIRouter()

class ContactRequest(BaseModel):
    name: str = Field(..., max_length=55)
    email: EmailStr
    company: str = Field(..., max_length=55)
    phone: str = Field(..., min_length=8, max_length=10)
    message: str
    services: list[str] = Field(default_factory=list)

    @field_validator("name", "company")
    @classmethod
    def validate_name_company(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("This field is required")

        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        value = value.strip()

        if not value.isdigit():
            raise ValueError("Phone number must contain digits only")

        if not 8 <= len(value) <= 10:
            raise ValueError("Phone number must be between 8 and 10 digits")

        return value

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        word_count = len(value.split())
        if not value:
            raise ValueError("Message is required")

        if word_count > 500:
            raise ValueError("Message must not exceed 500 words")

        return value

    @field_validator("services")
    @classmethod
    def validate_services(cls, value: list[str]) -> list[str]:
        # Remove empty/whitespace-only values
        services = [service.strip() for service in value if service.strip()]

        if len(services) == 0:
            raise ValueError("At least one service is required")

        return services




@router.post("/contact")
async def create_contact(request: ContactRequest):

    # Create contact record
    # contact = {
    #     "id": str(uuid4()),
    #     "partitionKey": "contact",
    #     "name": request.name,
    #     "email": request.email,
    #     "company": request.company,
    #     "phone": request.phone,
    #     "services": request.services,
    #     "message": request.message,
    #     "createdAt": datetime.now(timezone.utc).isoformat(),
    #     "status": "new",
    # }
    contact = {
        "id": str(uuid4()),
        "partitionKey": "contact",
        "name": request.name,
        "email": str(request.email),
        "company": request.company,
        "phone": request.phone,
        "services": request.services,
        "message": request.message,
        "createdAt": (
            datetime.now(timezone.utc)
            .isoformat()
        ),
        "status": "new",
        "emailStatus": "pending",
    }

    # Save to Cosmos DB
    saved_contact = save_contact(contact)

    try:

        send_contact_email(
            name=request.name,
            email=str(request.email),
            company=request.company,
            phone=request.phone,
            services=request.services,
            message=request.message,
        )

        email_status = "sent"

    except Exception as error:
        print(
            f"Failed to send contact email: {error}"
        )
        email_status = "failed"


    # -----------------------------------------------------
    # Return Response
    # -----------------------------------------------------

    return {
        "success": True,
        "message": (
            "Your enquiry has been submitted successfully."
        ),
        "data": {
            "id": saved_contact["id"],
            "emailStatus": email_status,
        },
    }