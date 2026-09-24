from azure.identity import AzureCliCredential

credential = AzureCliCredential()

token = credential.get_token(
    "https://management.azure.com/.default"
)

print("Azure CLI authentication successful!")
print(f"Token expires at: {token.expires_on}")