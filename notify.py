from datetime import datetime, timedelta
import socket
import psutil
import platform
import gspread
import uuid
import getpass
from oauth2client.service_account import ServiceAccountCredentials
from twilio.rest import Client
import schedule
import time
from dotenv import load_dotenv
import os
import json


load_dotenv()

creds_dict = {
    "type": os.getenv("GOOGLE_TYPE"),
    "project_id": os.getenv("GOOGLE_PROJECT_ID"),
    "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
    "private_key": os.getenv("GOOGLE_PRIVATE_KEY").replace('\\n', '\n'),
    "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
    "client_id": os.getenv("GOOGLE_CLIENT_ID"),
    "auth_uri": os.getenv("GOOGLE_AUTH_URI"),
    "token_uri": os.getenv("GOOGLE_TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("GOOGLE_AUTH_PROVIDER_CERT_URL"),
    "client_x509_cert_url": os.getenv("GOOGLE_CLIENT_CERT_URL")
}
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)


SPREADSHEET_KEY = "1UO_Gfv5JseIV7DYWficr4kY85j5WJ826HU6yjv5D2xQ"
log_sheet = client.open_by_key(SPREADSHEET_KEY).worksheet("Faults")

TWILIO_SID = "AC654714ee003ae41c011f0432c7387529"
TWILIO_AUTH_TOKEN = "4b5004b782570f60b1a6c9bd091bf4c5"
TWILIO_PHONE = "+1 903 296 3671"
TECH_PHONE = "+918754613017"

client_twilio = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

def get_laptop_status_rows():
    values = log_sheet.get_all_values()
    if not values:
        return []

    headers = values[0]
    data_rows = values[1:]

    result = []
    for i, row in enumerate(data_rows):
        row_dict = {headers[j]: row[j] if j < len(row) else "" for j in range(len(headers))}
        row_dict["row_index"] = i
        result.append(row_dict)

    return result

def send_reminder_sms_to_technician():
    print("Checking for unresolved faults to send SMS...")
    rows = get_laptop_status_rows()
    for i, row in enumerate(rows):
        if row.get("Fault Checked", "").strip().lower() == "no":
            name = row.get("Name", "Unknown")
            fault_desc = row.get("Fault Description", "Unknown")
            user_phone = row.get("Phone Number", "N/A")

            msg = (
                f"Unresolved fault reported by {name}:\n"
                f"- Issue: {fault_desc}\n"
                f"- Contact: {user_phone}"
            )
            try:
                client_twilio.messages.create(
                    body=msg,
                    from_=TWILIO_PHONE,
                    to=TECH_PHONE
                )
                print(f"Reminder sent for row {i + 2}")
            except Exception as e:
                print(f"Failed to send SMS for row {i + 2}: {e}")


