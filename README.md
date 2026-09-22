# Gmail Test Sender

A lightweight Python-based Gmail email automation tool designed for controlled email testing and validation of an IMAP email collection and analysis pipeline.

The tool sends configurable test emails through Gmail SMTP and supports different mail types, custom messages, attachments, multiple recipients, and batch sending.

## Features

* Gmail SMTP authentication
* Gmail App Password support
* Multiple recipient support
* To, CC and BCC
* Configurable email count
* Configurable delay between emails
* Predefined email templates
* Custom email subject
* Custom email message
* HTML email generation
* Attachment support
* Multiple attachments
* Unique test identifiers
* Internal test headers for correlation
* Sending status and activity logs
* CSV test reports
* Lightweight Tkinter GUI

## Supported Mail Types

The application currently supports:

* Account Notification
* Password Reset
* Invoice
* Order Confirmation
* Delivery Notification
* Security Notification
* HR Notification
* Subscription Renewal
* Newsletter
* Custom

The templates use generic test content and are intended for controlled laboratory testing.

## Architecture

```text
Gmail Test Sender
        |
        | SMTP
        v
   Gmail Account
        |
        | IMAP
        v
   IMAP Collector
        |
        v
 JSON / JSONL Data
        |
        v
      Splunk
```

The sender acts as a controlled source of test email data for the separate IMAP collection and analysis project.

## Requirements

* Python 3.10 or newer
* Gmail account
* Gmail 2-Step Verification
* Gmail App Password
* Windows, Linux or macOS

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd gmail-test-sender
```

Create the configuration file from the example:

```bash
copy config.example.json config.json
```

On Linux/macOS:

```bash
cp config.example.json config.json
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

Create a local `config.json` file:

```json
{
    "sender_email": "your-test-account@gmail.com",
    "app_password": "YOUR_GMAIL_APP_PASSWORD"
}
```

Do not commit `config.json` to GitHub.

The repository includes `config.example.json` as a safe configuration template.

## Gmail App Password

The application uses a Gmail App Password instead of storing the normal Gmail account password.

Before using the application:

1. Enable 2-Step Verification on the Gmail account.
2. Create an App Password.
3. Copy the generated App Password.
4. Add it to your local `config.json`.
5. Keep `config.json` out of version control.

Use a dedicated test Gmail account for laboratory testing.

## Running the Application

Start the application with:

```bash
python main.py
```

The GUI allows you to configure:

```text
Recipient
CC
BCC
Subject
Mail Count
Delay
Mail Type
Custom Message
Attachments
```

Then select:

```text
SEND EMAILS
```

## Custom Message Variables

Custom messages can use the following variables:

```text
{id}
{type}
{number}
{timestamp}
{date}
```

Example:

```text
Hello,

This is a test notification.

Reference: {id}
Message number: {number}
Type: {type}
Generated: {timestamp}

Regards,
Operations Team
```

The application replaces these variables automatically when sending the message.

## Attachments

T
