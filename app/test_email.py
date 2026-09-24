import os
from dotenv import load_dotenv
from azure.communication.email import EmailClient
from azure.identity import DefaultAzureCredential

load_dotenv();

client = EmailClient(
    endpoint=os.environ["EMAIL_ENDPOINT"],
    credential=DefaultAzureCredential()
)

message = {
    "senderAddress": os.environ["EMAIL_SENDER"],
    "recipients": {
        "to": [
            {
                "address": os.environ["EMAIL_RECIPIENT"]
            }
        ]
    },
    "content": {
        "subject": "Codeflux Test Email",
        "plainText": "Azure email is working!"
    }
}

poller = client.begin_send(message)

result = poller.result()

print("Email sent successfully!")
print(result)