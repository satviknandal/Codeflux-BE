from pathlib import Path
from datetime import datetime

TEMPLATE_PATH = (
    Path(__file__).resolve().parent.parent
    / "email_templates"
    / "contact_enquiry.html"
)


def render_contact_email(
    name: str,
    email: str,
    company: str,
    phone: str,
    services: list[str],
    message: str,
):
    template = TEMPLATE_PATH.read_text(encoding="utf-8")

    services_html = "<br>".join(
        f"• {service}" for service in services
    )

    return (
        template
        .replace("{{ title }}", "New Contact Enquiry")
        .replace(
            "{{ intro_message }}",
            "A new enquiry has been submitted through the Codeflux website."
        )
        .replace("{{ name }}", name)
        .replace("{{ email }}", email)
        .replace("{{ company }}", company or "Not provided")
        .replace("{{ phone }}", phone)
        .replace("{{ services }}", services_html)
        .replace("{{ message }}", message)
        .replace("{{ year }}", str(datetime.now().year))
    )