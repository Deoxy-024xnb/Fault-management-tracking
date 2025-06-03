from flask import Flask, render_template, request, redirect, url_for, flash
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException
from dotenv import load_dotenv
import os
import json

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

# Google Sheets Setup
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

# Open your spreadsheet
spreadsheet_id = "1UO_Gfv5JseIV7DYWficr4kY85j5WJ826HU6yjv5D2xQ"
sheet = client.open_by_key(spreadsheet_id)

fault_sheet = sheet.worksheet("Faults")
subscription_sheet = sheet.worksheet("Renewals")

def validate_phone(country_code, number):
    full_number = country_code + number
    try:
        parsed = phonenumbers.parse(full_number, None)
        return phonenumbers.is_valid_number(parsed)
    except NumberParseException:
        return False

def update_days_since_reported():
    all_rows = fault_sheet.get_all_values()
    
    for i, row in enumerate(all_rows[1:], start=2):
        fault_date_str = row[0]  
        fault_checked = row[3].strip().lower() if len(row) > 3 else 'no'  
        days_since = '-'

        if fault_checked != 'yes':
            try:
                fault_date = datetime.strptime(fault_date_str, '%Y-%m-%d')
                days_since = (datetime.now() - fault_date).days
            except Exception:
                days_since = '0'  

        if len(row) < 6:
            fault_sheet.update_cell(i, 6, str(days_since))
        else:
            fault_sheet.update_cell(i, 6, str(days_since))

@app.route('/')
def index():
    update_days_since_reported()
    return render_template('index.html')

@app.route('/fault-report', methods=['GET', 'POST'])
def fault_report():
    country_options = [
        {"name": "United States", "code": "+1"},
        {"name": "United Kingdom", "code": "+44"},
        {"name": "India", "code": "+91"},
        {"name": "Australia", "code": "+61"},
        {"name": "Germany", "code": "+49"},
        {"name": "France", "code": "+33"},
        {"name": "Japan", "code": "+81"},
        {"name": "Canada", "code": "+1"},
        {"name": "China", "code": "+86"},
        {"name": "Brazil", "code": "+55"},
        {"name": "South Africa", "code": "+27"},
        {"name": "Russia", "code": "+7"},
        {"name": "Mexico", "code": "+52"},
        {"name": "Italy", "code": "+39"},
        {"name": "Spain", "code": "+34"},
    ]

    if request.method == 'POST':
        name = request.form['name'].strip()
        fault_desc = request.form['fault_description'].strip()
        country_code = request.form['country_code']
        phone_number = request.form['phone_number'].strip()

        # Validate phone number
        if not validate_phone(country_code, phone_number):
            flash("Invalid phone number for selected country code. Please enter a valid number.")
            return render_template('fault_report.html', country_options=country_options)

        all_rows = fault_sheet.get_all_values()
        for row in all_rows[1:]:  
            if len(row) >= 3 and row[1].strip().lower() == name.lower() and row[2].strip().lower() == fault_desc.lower():
                flash("You've already raised a complaint. A technician will reach out to you soon.")
                return render_template('fault_report.html', country_options=country_options)
            
        fault_checked = 'No'  
        today_date = datetime.now().strftime('%Y-%m-%d')

        fault_sheet.append_row([today_date, name, fault_desc, fault_checked, country_code + phone_number, '0'])
        update_days_since_reported()
        return redirect(url_for('index'))

    return render_template('fault_report.html', country_options=country_options)

@app.route('/subscription-renewal', methods=['GET', 'POST'])
def subscription_renewal():
    country_options = [
        {"name": "United States", "code": "+1"},
        {"name": "United Kingdom", "code": "+44"},
        {"name": "India", "code": "+91"},
        {"name": "Australia", "code": "+61"},
        {"name": "Germany", "code": "+49"},
        {"name": "France", "code": "+33"},
        {"name": "Japan", "code": "+81"},
        {"name": "Canada", "code": "+1"},
        {"name": "China", "code": "+86"},
        {"name": "Brazil", "code": "+55"},
        {"name": "South Africa", "code": "+27"},
        {"name": "Russia", "code": "+7"},
        {"name": "Mexico", "code": "+52"},
        {"name": "Italy", "code": "+39"},
        {"name": "Spain", "code": "+34"},
    ]

    if request.method == 'POST':
        user_name = request.form['user_name'].strip()
        software_name = request.form['software_name'].strip()
        country_code = request.form['country_code']
        phone_number = request.form['phone_number'].strip()
        expiry_date = request.form['expiry_date']
        
        if not user_name:
            flash("Please enter your name")
            return render_template('subscription_renewal.html', country_options=country_options)

        if not validate_phone(country_code, phone_number):
            flash("Invalid phone number for selected country code. Please enter a valid number.")
            return render_template('subscription_renewal.html', country_options=country_options)

        all_rows = subscription_sheet.get_all_values()
        for row in all_rows[1:]:
            if len(row) >= 2 and row[0].strip().lower() == user_name.lower() and row[1].strip().lower() == software_name.lower():
                flash("You have already submitted this software subscription. Please check again.")
                return render_template('subscription_renewal.html', country_options=country_options)

        today = datetime.now().date()
        days_left = (datetime.strptime(expiry_date, '%Y-%m-%d').date() - today).days
        
        subscription_sheet.append_row([
            user_name, 
            software_name, 
            expiry_date, 
            str(days_left),
            country_code + phone_number
        ])
        return redirect(url_for('index'))
        
    return render_template('subscription_renewal.html', country_options=country_options)


if __name__ == '__main__':
    app.run(debug=True)
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))