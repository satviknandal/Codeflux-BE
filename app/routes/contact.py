from datetime import datetime, timezone
from uuid import uuid4
import logging

from fastapi import APIRouter
from pydantic import BaseModel, EmailStr, Field, field_validator

from app.database.cosmos import save_contact
from app.services.email import send_confirmation_email, send_contact_email


router = APIRouter()

logger = logging.getLogger(__name__)


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
            raise ValueError(
                "Phone number must be between 8 and 10 digits"
            )

        return value

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Message is required")

        word_count = len(value.split())

        if word_count > 500:
            raise ValueError(
                "Message must not exceed 500 words"
            )

        return value

    @field_validator("services")
    @classmethod
    def validate_services(cls, value: list[str]) -> list[str]:
        services = [
            service.strip()
            for service in value
            if service.strip()
        ]

        if len(services) == 0:
            raise ValueError(
                "At least one service is required"
            )

        return services


def generate_reference_number() -> str:
    date_part = datetime.now(timezone.utc).strftime("%Y%m%d")
    unique_part = uuid4().hex[:8].upper()

    return f"CF-{date_part}-{unique_part}"


@router.post("/api/contact")
async def create_contact(request: ContactRequest):

    reference_number = generate_reference_number()

    logger.info(
        "Contact request received. referenceNumber=%s",
        reference_number,
    )

    contact = {
        "id": str(uuid4()),
        "referenceNumber": reference_number,
        "partitionKey": "contact",
        "name": request.name,
        "email": str(request.email),
        "company": request.company,
        "phone": request.phone,
        "services": request.services,
        "message": request.message,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "status": "new",
        "emailStatus": "pending",
    }

    # -----------------------------------------------------
    # Save to Cosmos DB
    # -----------------------------------------------------

    try:
        logger.info(
            "Saving contact to Cosmos DB. referenceNumber=%s",
            reference_number,
        )

        saved_contact = save_contact(contact)

        logger.info(
            "Contact saved successfully. referenceNumber=%s",
            reference_number,
        )

    except Exception:
        logger.exception(
            "Failed to save contact to Cosmos DB. "
            "referenceNumber=%s",
            reference_number,
        )

        raise

    # -----------------------------------------------------
    # Send internal contact email
    # -----------------------------------------------------

    email_status = "failed"

    try:
        logger.info(
            "Sending contact notification email. "
            "referenceNumber=%s",
            reference_number,
        )

        send_contact_email(
            reference_number=reference_number,
            name=request.name,
            email=str(request.email),
            company=request.company,
            phone=request.phone,
            services=request.services,
            message=request.message,
        )

        email_status = "accepted"

        logger.info(
            "Contact notification email accepted. "
            "referenceNumber=%s",
            reference_number,
        )

    except Exception:
        logger.exception(
            "Failed to send contact notification email. "
            "referenceNumber=%s",
            reference_number,
        )

    # -----------------------------------------------------
    # Send customer confirmation email
    # -----------------------------------------------------

    confirmation_email_status = "failed"

    try:
        logger.info(
            "Sending confirmation email. "
            "referenceNumber=%s",
            reference_number,
        )

        send_confirmation_email(
            reference_number=reference_number,
            name=request.name,
            email=str(request.email),
            company=request.company,
            phone=request.phone,
            services=request.services,
            message=request.message,
        )

        confirmation_email_status = "accepted"

        logger.info(
            "Confirmation email accepted. "
            "referenceNumber=%s",
            reference_number,
        )

    except Exception:
        logger.exception(
            "Failed to send confirmation email. "
            "referenceNumber=%s",
            reference_number,
        )

    # -----------------------------------------------------
    # Return Response
    # -----------------------------------------------------

    logger.info(
        "Contact request completed. "
        "referenceNumber=%s, emailStatus=%s, "
        "confirmationEmailStatus=%s",
        reference_number,
        email_status,
        confirmation_email_status,
    )

    return {
        "success": True,
        "message": (
            "Your enquiry has been submitted successfully."
        ),
        "data": {
            "id": saved_contact["id"],
            "referenceNumber": reference_number,
            "emailStatus": email_status,
            "confirmationEmailStatus": (
                confirmation_email_status
            ),
        },
    }