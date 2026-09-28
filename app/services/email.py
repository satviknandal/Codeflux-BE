import os
from datetime import datetime
from pathlib import Path
from html import escape

from azure.communication.email import EmailClient
from azure.identity import DefaultAzureCredential


# ---------------------------------------------------------
# Azure Communication Services Email Client
# ---------------------------------------------------------

client = EmailClient(
    endpoint=os.environ["EMAIL_ENDPOINT"],
    credential=DefaultAzureCredential(),
)


# ---------------------------------------------------------
# Email Template
# ---------------------------------------------------------

TEMPLATE_PATH = (
    Path(__file__).resolve().parent.parent
    / "email_templates"
    / "contact_enquiry.html"
)


# ---------------------------------------------------------
# Render Contact Email
# ---------------------------------------------------------

def render_contact_email(
    name: str,
    email: str,
    company: str,
    phone: str,
    services: list[str],
    message: str,
) -> str:

    template = TEMPLATE_PATH.read_text(
        encoding="utf-8"
    )

    # Escape user-provided content before putting it
    # into HTML.

    safe_name = escape(name)

    safe_email = escape(email)

    safe_company = escape(
        company or "Not provided"
    )

    safe_phone = escape(phone)

    safe_message = escape(message)

    # Services

    services_html = "<br>".join(
        f"• {escape(service)}"
        for service in services
    )

    # Replace template placeholders

    html_content = (
        template
        .replace(
            "{{ title }}",
            "New Contact Enquiry"
        )
        .replace(
            "{{ intro_message }}",
            "A new enquiry has been submitted through the Codeflux website."
        )
        .replace(
            "{{ name }}",
            safe_name
        )
        .replace(
            "{{ email }}",
            safe_email
        )
        .replace(
            "{{ company }}",
            safe_company
        )
        .replace(
            "{{ phone }}",
            safe_phone
        )
        .replace(
            "{{ services }}",
            services_html
        )
        .replace(
            "{{ message }}",
            safe_message
        )
        .replace(
            "{{ year }}",
            str(datetime.now().year)
        )
    )

    return html_content


# ---------------------------------------------------------
# Plain Text Version
# ---------------------------------------------------------

def create_plain_text_email(
    name: str,
    email: str,
    company: str,
    phone: str,
    services: list[str],
    message: str,
) -> str:

    services_text = "\n".join(
        f"- {service}"
        for service in services
    )

    return f"""
New Contact Enquiry
===================

A new enquiry has been submitted through the Codeflux website.

Name:
{name}

Email:
{email}

Company:
{company or "Not provided"}

Phone:
{phone}

Services:
{services_text}

Message:
{message}

===================

Codeflux
AI & Software Development
""".strip()


# ---------------------------------------------------------
# Send Contact Email
# ---------------------------------------------------------

def send_contact_email(
    name: str,
    email: str,
    company: str,
    phone: str,
    services: list[str],
    message: str,
):

    html_content = render_contact_email(
        name=name,
        email=email,
        company=company,
        phone=phone,
        services=services,
        message=message,
    )

    plain_text_content = create_plain_text_email(
        name=name,
        email=email,
        company=company,
        phone=phone,
        services=services,
        message=message,
    )

    email_message = {
        "senderAddress": os.environ["EMAIL_SENDER"],

        "recipients": {
            "to": [
                {
                    "address": os.environ[
                        "EMAIL_RECIPIENT"
                    ]
                }
            ]
        },

        "content": {
            "subject": (
                f"New Contact Enquiry - {name}"
            ),

            "plainText": plain_text_content,

            "html": html_content,
        },

        # When support clicks Reply,
        # the reply will go directly
        # to the person who submitted
        # the enquiry.

        "replyTo": [
            {
                "address": email,
                "displayName": name,
            }
        ],
    }

    poller = client.begin_send(
        email_message
    )

    return poller.result()


def send_confirmation_email(
    reference_number: str,
    name: str,
    email: str,
    services: list[str],
):
    template_path = (
        Path(__file__).resolve().parent.parent
        / "email_templates"
        / "contact_confirmation.html"
    )

    template = template_path.read_text(encoding="utf-8")

    safe_name = escape(name)
    safe_reference = escape(reference_number)

    services_html = "<br>".join(
        f"• {escape(service)}"
        for service in services
    )

    html_content = (
        template
        .replace("{{ name }}", safe_name)
        .replace("{{ reference_number }}", safe_reference)
        .replace("{{ services }}", services_html)
    )

    plain_text_content = f"""
Hi {name},

Thank you for contacting Codeflux.

We have successfully received your enquiry and our team will review it shortly.

Reference Number:
{reference_number}

Services requested:
{", ".join(services)}

If you need to follow up regarding your enquiry, please quote the reference number above.

Our team will get back to you as soon as possible.

Kind regards,
Codeflux Team
AI & Software Development

https://codeflux.com.au
""".strip()

    email_message = {
        "senderAddress": os.environ["EMAIL_SENDER"],

        "recipients": {
            "to": [
                {
                    "address": email,
                    "displayName": name,
                }
            ]
        },

        "content": {
            "subject": f"Codeflux Enquiry Received – Ref: {reference_number}",
            "plainText": plain_text_content,
            "html": html_content,
        },
    }

    poller = client.begin_send(email_message)

    return poller.result()