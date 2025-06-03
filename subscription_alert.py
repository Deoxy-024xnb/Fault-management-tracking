import os
from twilio.rest import Client
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from dotenv import load_dotenv
import os
import json

# Google Sheets Setup

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

# Open the spreadsheet
spreadsheet_id = "1UO_Gfv5JseIV7DYWficr4kY85j5WJ826HU6yjv5D2xQ"
sheet = client.open_by_key(spreadsheet_id)
subscription_sheet = sheet.worksheet("Renewals")

# Twilio configuration
account_sid = os.getenv("ACCOUNT_SID")
auth_token = os.getenv("AUTH_TOKEN")
twilio_phone_number = '+16184238246'

twilio_client = Client(account_sid, auth_token)

def update_days_left():
    """Update the days left for each subscription"""
    all_rows = subscription_sheet.get_all_values()
    today = datetime.now().date()
    
    for i, row in enumerate(all_rows[1:], start=2):
        try:
            expiry_date = datetime.strptime(row[2], '%Y-%m-%d').date()  
            days_left = (expiry_date - today).days
            subscription_sheet.update_cell(i, 4, str(days_left))  
        except (ValueError, IndexError):
            print(f"Error processing row {i}: {row}")
            continue

def send_renewal_alerts():
    """Send SMS alerts for subscriptions with less than 10 days left"""
    all_rows = subscription_sheet.get_all_values()
    
    # Skip header row
    for row in all_rows[1:]:
        try:
            user_name = row[0]
            software_name = row[1]
            days_left = int(row[3])  
            phone_number = row[4]     
            
            if days_left <= 10 and days_left >= 0:
                message = (
                    f"Hello {user_name}, \n"
                    f"Your subscription for {software_name} will expire in {days_left} days. "
                    f"Please renew your subscription to avoid service interruption."
                )
                
                try:
                    twilio_client.messages.create(
                        body=message,
                        from_=twilio_phone_number,
                        to=phone_number
                    )
                    print(f"Alert sent to {user_name} for {software_name}")
                except Exception as e:
                    print(f"Error sending message to {phone_number}: {str(e)}")
                    
        except (ValueError, IndexError) as e:
            print(f"Error processing row: {row}. Error: {str(e)}")
            continue

def main():
    try:
        print("Updating days left for subscriptions...")
        update_days_left()
        
        print("Sending renewal alerts...")
        send_renewal_alerts()
        
        print("Process completed successfully!")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()