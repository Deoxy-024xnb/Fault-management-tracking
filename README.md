# Device Fault Tracking and Subscription Management System

This project provides a simple yet powerful web-based system for tracking device faults and managing software subscription renewals. It includes:

- A **Flask web interface** for submitting fault reports and subscription logs.
- Integration with **Google Sheets** for data storage and tracking.
- **Twilio SMS alerts** to notify technicians of unresolved faults.
- A **daily scheduler** to automate notifications.
- A **subscription tracker** that calculates days left and reminds users accordingly.

---

## 📁 Project Structure

```

fault\_tracking\_management/
├── web\_app.py               # Flask app for form-based submission
├── notify.py                # Twilio SMS integration for fault alerts
├── scheduler.py             # Background scheduler (24-hour reminders)
├── subscription\_alert.py    # Handles subscription days left and alerts
├── requirements.txt         # Python dependencies
├── .env                     # Contains sensitive config like API keys

````

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/Fault-management-tracking.git
cd Fault-management-tracking/fault_tracking_management
````

### 2. Install Dependencies

Make sure you have Python 3.7+ installed.

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
GOOGLE_SHEET_WEBHOOK_URL=your_webhook_url_here
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890
TO_PHONE_NUMBER=+0987654321
```

> 🔐 **Important:** Never share your `.env` file or push it to GitHub.

---

## 🧪 Running the Application

### Start the Flask App

```bash
python web_app.py
```

Visit `http://localhost:5000` in your browser.

---

### Start the Scheduler

This will send reminders every 24 hours for unresolved faults.

```bash
python scheduler.py
```

---

## 📝 Google Sheet Setup

1. Create a Google Sheet with columns like:

   * `DeviceID`
   * `Fault Description`
   * `Faults Checked or Not`

2. Link the sheet with a **Google Apps Script** webhook that your `web_app.py` sends data to.

> ✏️ Make sure you **replace** the default `GOOGLE_SHEET_WEBHOOK_URL` in `.env` with your actual webhook URL.

---

## 🔔 Twilio Setup

1. [Sign up for Twilio](https://www.twilio.com/).
2. Get your `ACCOUNT_SID`, `AUTH_TOKEN`, and a Twilio phone number.
3. Replace the placeholders in the `.env` file.

---

## ✅ Features

* Submit fault reports and log renewals via a web UI.
* Store reports in Google Sheets.
* Automatically notify technicians via SMS.
* Calculate days left for Microsoft 365 or antivirus subscriptions.

---

## 📌 To-Do / Future Improvements

* Add user authentication
* Web dashboard with search/filtering
* Email integration for non-SMS users
* Machine learning for fault prioritization (optional)

---

## Hosted Website

https://private-fault-management.onrender.com/

