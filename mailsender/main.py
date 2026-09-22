import csv
import json
import mimetypes
import os
import smtplib
import ssl
import time
import tkinter as tk
from datetime import datetime
from email.message import EmailMessage
from email.utils import formatdate, make_msgid
from threading import Thread
from tkinter import filedialog, messagebox, ttk
from uuid import uuid4


with open("config.json", "r", encoding="utf-8") as file:
    config = json.load(file)

SENDER_EMAIL = config["sender_email"]
APP_PASSWORD = config["app_password"]


class GmailTestSender:
    def __init__(self, root):
        self.root = root
        self.root.title("Gmail Mail Sender V4")
        self.root.geometry("950x850")
        self.root.minsize(900, 800)

        self.attachments = []
        self.results = []

        self.mail_types = [
            "Account Notification",
            "Password Reset",
            "Invoice",
            "Order Confirmation",
            "Delivery Notification",
            "Security Notification",
            "HR Notification",
            "Subscription Renewal",
            "Newsletter",
            "Custom"
        ]

        self.build_ui()

    def build_ui(self):
        main = ttk.Frame(self.root, padding=18)
        main.pack(fill="both", expand=True)

        ttk.Label(
            main,
            text="Gmail Mail Sender V4",
            font=("Segoe UI", 20, "bold")
        ).pack(anchor="w", pady=(0, 15))

        details = ttk.LabelFrame(
            main,
            text="Mail Configuration",
            padding=12
        )
        details.pack(fill="x", pady=(0, 12))

        ttk.Label(
            details,
            text="Recipient"
        ).grid(row=0, column=0, sticky="w", pady=5)

        self.to_entry = ttk.Entry(details)
        self.to_entry.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=10,
            pady=5
        )

        ttk.Label(
            details,
            text="CC"
        ).grid(row=1, column=0, sticky="w", pady=5)

        self.cc_entry = ttk.Entry(details)
        self.cc_entry.grid(
            row=1,
            column=1,
            sticky="ew",
            padx=10,
            pady=5
        )

        ttk.Label(
            details,
            text="BCC"
        ).grid(row=2, column=0, sticky="w", pady=5)

        self.bcc_entry = ttk.Entry(details)
        self.bcc_entry.grid(
            row=2,
            column=1,
            sticky="ew",
            padx=10,
            pady=5
        )

        ttk.Label(
            details,
            text="Subject"
        ).grid(row=3, column=0, sticky="w", pady=5)

        self.subject_entry = ttk.Entry(details)
        self.subject_entry.grid(
            row=3,
            column=1,
            sticky="ew",
            padx=10,
            pady=5
        )

        ttk.Label(
            details,
            text="Mail Count"
        ).grid(row=4, column=0, sticky="w", pady=5)

        self.count_entry = ttk.Entry(
            details,
            width=15
        )
        self.count_entry.insert(0, "1")
        self.count_entry.grid(
            row=4,
            column=1,
            sticky="w",
            padx=10,
            pady=5
        )

        ttk.Label(
            details,
            text="Delay (seconds)"
        ).grid(row=5, column=0, sticky="w", pady=5)

        self.delay_entry = ttk.Entry(
            details,
            width=15
        )
        self.delay_entry.insert(0, "2")
        self.delay_entry.grid(
            row=5,
            column=1,
            sticky="w",
            padx=10,
            pady=5
        )

        details.columnconfigure(1, weight=1)

        type_frame = ttk.LabelFrame(
            main,
            text="Mail Type",
            padding=12
        )
        type_frame.pack(
            fill="x",
            pady=(0, 12)
        )

        ttk.Label(
            type_frame,
            text="Select Mail Type"
        ).pack(
            side="left",
            padx=(0, 12)
        )

        self.mail_type_var = tk.StringVar(
            value="Account Notification"
        )

        self.mail_type_combo = ttk.Combobox(
            type_frame,
            textvariable=self.mail_type_var,
            values=self.mail_types,
            state="readonly",
            width=30
        )
        self.mail_type_combo.pack(
            side="left"
        )

        self.mail_type_combo.bind(
            "<<ComboboxSelected>>",
            self.mail_type_changed
        )

        body_frame = ttk.LabelFrame(
            main,
            text="Message",
            padding=12
        )
        body_frame.pack(
            fill="both",
            expand=True,
            pady=(0, 12)
        )

        self.message_box = tk.Text(
            body_frame,
            height=14,
            wrap="word"
        )
        self.message_box.pack(
            fill="both",
            expand=True
        )

        self.load_template(
            "Account Notification"
        )

        attachment_frame = ttk.LabelFrame(
            main,
            text="Attachments",
            padding=12
        )
        attachment_frame.pack(
            fill="x",
            pady=(0, 12)
        )

        ttk.Button(
            attachment_frame,
            text="Add Files",
            command=self.add_files
        ).pack(side="left")

        ttk.Button(
            attachment_frame,
            text="Clear",
            command=self.clear_files
        ).pack(
            side="left",
            padx=8
        )

        self.attachment_label = ttk.Label(
            attachment_frame,
            text="No attachments"
        )
        self.attachment_label.pack(
            side="left",
            padx=10
        )

        action_frame = ttk.Frame(main)
        action_frame.pack(
            fill="x",
            pady=(0, 12)
        )

        self.send_button = ttk.Button(
            action_frame,
            text="SEND EMAILS",
            command=self.start_sending
        )
        self.send_button.pack(
            side="left",
            ipadx=20,
            ipady=6
        )

        self.progress_label = ttk.Label(
            action_frame,
            text="Ready"
        )
        self.progress_label.pack(
            side="right"
        )

        log_frame = ttk.LabelFrame(
            main,
            text="Activity Log",
            padding=8
        )
        log_frame.pack(
            fill="both",
            expand=True,
            pady=(0, 12)
        )

        self.log_box = tk.Text(
            log_frame,
            height=10,
            state="disabled",
            wrap="word"
        )
        self.log_box.pack(
            fill="both",
            expand=True
        )

        summary_frame = ttk.LabelFrame(
            main,
            text="Summary",
            padding=8
        )
        summary_frame.pack(
            fill="x"
        )

        self.summary_label = ttk.Label(
            summary_frame,
            text="SENT: 0    FAILED: 0    TOTAL: 0"
        )
        self.summary_label.pack(
            anchor="w"
        )

    def templates(self):
        return {
            "Account Notification": {
                "subject": "Your account activity summary",
                "body": (
                    "Hello,\n\n"
                    "Your account activity summary is now available "
                    "for review.\n\n"
                    "You can review your recent activity by visiting:\n"
                    "https://example.com/account\n\n"
                    "If you have any questions, please contact "
                    "the support team.\n\n"
                    "Regards,\n"
                    "Customer Support"
                )
            },
            "Password Reset": {
                "subject": "Password reset request",
                "body": (
                    "Hello,\n\n"
                    "We received a request to reset the password "
                    "associated with your account.\n\n"
                    "If you made this request, continue here:\n"
                    "https://example.com/reset\n\n"
                    "If you did not request a password reset, "
                    "you can safely ignore this message.\n\n"
                    "Regards,\n"
                    "Account Support"
                )
            },
            "Invoice": {
                "subject": "Invoice available for review",
                "body": (
                    "Hello,\n\n"
                    "Your latest invoice is now available for review.\n\n"
                    "Invoice reference: INV-{number}\n"
                    "Amount: 245.00\n"
                    "Due date: {date}\n\n"
                    "You can review the invoice here:\n"
                    "https://example.com/invoice\n\n"
                    "Regards,\n"
                    "Billing Department"
                )
            },
            "Order Confirmation": {
                "subject": "Order confirmation",
                "body": (
                    "Hello,\n\n"
                    "Thank you for your order.\n\n"
                    "Order reference: ORD-{number}\n"
                    "Status: Confirmed\n\n"
                    "You can review your order details here:\n"
                    "https://example.com/orders\n\n"
                    "Regards,\n"
                    "Customer Services"
                )
            },
            "Delivery Notification": {
                "subject": "Delivery status update",
                "body": (
                    "Hello,\n\n"
                    "There has been an update to the delivery "
                    "status of your recent order.\n\n"
                    "Tracking reference: TRK-{number}\n"
                    "Current status: In transit\n\n"
                    "View delivery details:\n"
                    "https://example.com/delivery\n\n"
                    "Regards,\n"
                    "Delivery Support"
                )
            },
            "Security Notification": {
                "subject": "Security notification",
                "body": (
                    "Hello,\n\n"
                    "A recent security-related event was detected "
                    "on your account.\n\n"
                    "Please review your recent activity:\n"
                    "https://example.com/security\n\n"
                    "If you do not recognize the activity, "
                    "contact support.\n\n"
                    "Regards,\n"
                    "Security Team"
                )
            },
            "HR Notification": {
                "subject": "Employee information update",
                "body": (
                    "Hello,\n\n"
                    "An updated employee information notice is "
                    "available for review.\n\n"
                    "Please review the information here:\n"
                    "https://example.com/hr\n\n"
                    "Regards,\n"
                    "Human Resources"
                )
            },
            "Subscription Renewal": {
                "subject": "Subscription renewal reminder",
                "body": (
                    "Hello,\n\n"
                    "Your subscription is scheduled for renewal.\n\n"
                    "Renewal date: {date}\n"
                    "Reference: SUB-{number}\n\n"
                    "Review your subscription details:\n"
                    "https://example.com/subscription\n\n"
                    "Regards,\n"
                    "Customer Services"
                )
            },
            "Newsletter": {
                "subject": "Monthly technology newsletter",
                "body": (
                    "Hello,\n\n"
                    "Here is your monthly technology newsletter.\n\n"
                    "This month's topics include security, "
                    "cloud technology, and software updates.\n\n"
                    "Read the latest edition:\n"
                    "https://example.com/newsletter\n\n"
                    "Regards,\n"
                    "Technology Updates"
                )
            }
        }

    def load_template(self, mail_type):
        if mail_type == "Custom":
            self.subject_entry.delete(
                0,
                "end"
            )

            self.message_box.delete(
                "1.0",
                "end"
            )

            return

        template = self.templates()[mail_type]

        self.subject_entry.delete(
            0,
            "end"
        )

        self.subject_entry.insert(
            0,
            template["subject"]
        )

        self.message_box.delete(
            "1.0",
            "end"
        )

        self.message_box.insert(
            "1.0",
            template["body"]
        )

    def mail_type_changed(self, event=None):
        self.load_template(
            self.mail_type_var.get()
        )

    def add_files(self):
        files = filedialog.askopenfilenames(
            title="Select Attachments"
        )

        for path in files:
            if path not in self.attachments:
                self.attachments.append(path)

        self.update_attachment_label()

    def clear_files(self):
        self.attachments.clear()
        self.update_attachment_label()

    def update_attachment_label(self):
        if not self.attachments:
            self.attachment_label.config(
                text="No attachments"
            )
            return

        names = [
            os.path.basename(path)
            for path in self.attachments
        ]

        self.attachment_label.config(
            text=", ".join(names)
        )

    def log(self, text):
        def update():
            self.log_box.config(
                state="normal"
            )

            self.log_box.insert(
                "end",
                text + "\n"
            )

            self.log_box.see("end")

            self.log_box.config(
                state="disabled"
            )

        self.root.after(
            0,
            update
        )

    def set_progress(self, text):
        self.root.after(
            0,
            lambda: self.progress_label.config(
                text=text
            )
        )

    def get_addresses(self, value):
        return [
            item.strip()
            for item in value.split(",")
            if item.strip()
        ]

    def generate_test_id(
        self,
        mail_type,
        number
    ):
        return (
            f"MAIL-{mail_type.upper().replace(' ', '-')}-"
            f"{datetime.now().strftime('%Y%m%d%H%M%S')}-"
            f"{number:03d}-"
            f"{uuid4().hex[:6].upper()}"
        )

    def add_attachment(
        self,
        message,
        path
    ):
        if not os.path.isfile(path):
            return

        mime_type, encoding = mimetypes.guess_type(
            path
        )

        if mime_type is None:
            mime_type = "application/octet-stream"

        maintype, subtype = mime_type.split(
            "/",
            1
        )

        with open(
            path,
            "rb"
        ) as file:
            data = file.read()

        message.add_attachment(
            data,
            maintype=maintype,
            subtype=subtype,
            filename=os.path.basename(path)
        )

    def create_message(
        self,
        mail_type,
        recipient,
        cc,
        bcc,
        number
    ):
        test_id = self.generate_test_id(
            mail_type,
            number
        )

        timestamp = datetime.now().isoformat(
            timespec="seconds"
        )

        date_value = datetime.now().strftime(
            "%Y-%m-%d"
        )

        message = EmailMessage()

        message["From"] = SENDER_EMAIL
        message["To"] = ", ".join(recipient)

        if cc:
            message["Cc"] = ", ".join(cc)

        if mail_type == "Custom":
            subject = self.subject_entry.get().strip()

            body = self.message_box.get(
                "1.0",
                "end-1c"
            )

        else:
            template = self.templates()[mail_type]

            subject = template["subject"]

            body = template["body"]

        body = (
            body
            .replace(
                "{id}",
                test_id
            )
            .replace(
                "{type}",
                mail_type
            )
            .replace(
                "{number}",
                str(number)
            )
            .replace(
                "{timestamp}",
                timestamp
            )
            .replace(
                "{date}",
                date_value
            )
        )

        subject = (
            subject
            .replace(
                "{id}",
                test_id
            )
            .replace(
                "{type}",
                mail_type
            )
            .replace(
                "{number}",
                str(number)
            )
        )

        message["Subject"] = subject
        message["Date"] = formatdate(
            localtime=True
        )
        message["Message-ID"] = make_msgid()

        message["X-Test-ID"] = test_id
        message["X-Test-Type"] = mail_type
        message["X-Test-Number"] = str(number)
        message["X-Test-Timestamp"] = timestamp

        message.set_content(body)

        if mail_type in (
            "HTML",
            "Account Notification",
            "Password Reset",
            "Invoice",
            "Order Confirmation",
            "Delivery Notification",
            "Security Notification",
            "HR Notification",
            "Subscription Renewal",
            "Newsletter"
        ):
            html_body = (
                "<html>"
                "<body>"
                "<p>"
                + body.replace(
                    "\n",
                    "<br>"
                )
                + "</p>"
                "</body>"
                "</html>"
            )

            message.add_alternative(
                html_body,
                subtype="html"
            )

        if mail_type in (
            "Attachment",
            "Multipart"
        ):
            for path in self.attachments:
                self.add_attachment(
                    message,
                    path
                )

        return message, test_id

    def start_sending(self):
        recipient = self.to_entry.get().strip()

        if not recipient:
            messagebox.showerror(
                "Missing Recipient",
                "Enter a recipient email address."
            )
            return

        try:
            count = int(
                self.count_entry.get()
            )

            delay = float(
                self.delay_entry.get()
            )

        except ValueError:
            messagebox.showerror(
                "Invalid Input",
                "Mail Count must be an integer "
                "and Delay must be a number."
            )
            return

        if count < 1:
            messagebox.showerror(
                "Invalid Mail Count",
                "Mail Count must be at least 1."
            )
            return

        if delay < 0:
            messagebox.showerror(
                "Invalid Delay",
                "Delay cannot be negative."
            )
            return

        if not self.subject_entry.get().strip():
            messagebox.showerror(
                "Missing Subject",
                "Enter a subject."
            )
            return

        self.results.clear()

        self.send_button.config(
            state="disabled"
        )

        thread = Thread(
            target=self.send_emails,
            args=(count, delay),
            daemon=True
        )

        thread.start()

    def send_emails(
        self,
        count,
        delay
    ):
        recipient = self.get_addresses(
            self.to_entry.get()
        )

        cc = self.get_addresses(
            self.cc_entry.get()
        )

        bcc = self.get_addresses(
            self.bcc_entry.get()
        )

        mail_type = self.mail_type_var.get()

        try:
            context = ssl.create_default_context()

            self.set_progress(
                "Connecting to Gmail..."
            )

            with smtplib.SMTP(
                "smtp.gmail.com",
                587,
                timeout=30
            ) as server:

                server.ehlo()

                server.starttls(
                    context=context
                )

                server.ehlo()

                server.login(
                    SENDER_EMAIL,
                    APP_PASSWORD
                )

                self.log(
                    "================================"
                )

                self.log(
                    "Gmail authentication successful."
                )

                self.log(
                    f"Mail Type: {mail_type}"
                )

                self.log(
                    f"Mail Count: {count}"
                )

                self.log(
                    "================================"
                )

                sent = 0
                failed = 0

                for number in range(
                    1,
                    count + 1
                ):
                    self.set_progress(
                        f"Sending {number}/{count}"
                    )

                    try:
                        message, test_id = (
                            self.create_message(
                                mail_type,
                                recipient,
                                cc,
                                bcc,
                                number
                            )
                        )

                        server.send_message(
                            message,
                            from_addr=SENDER_EMAIL,
                            to_addrs=(
                                recipient
                                + cc
                                + bcc
                            )
                        )

                        sent += 1

                        self.results.append({
                            "test_id": test_id,
                            "mail_type": mail_type,
                            "number": number,
                            "status": "SENT",
                            "message_id": message[
                                "Message-ID"
                            ],
                            "timestamp": datetime.now().isoformat(
                                timespec="seconds"
                            ),
                            "error": ""
                        })

                        self.log(
                            f"[+] {number}/{count} SENT"
                        )

                        self.log(
                            f"    ID: {test_id}"
                        )

                    except Exception as error:
                        failed += 1

                        self.results.append({
                            "test_id": "N/A",
                            "mail_type": mail_type,
                            "number": number,
                            "status": "FAILED",
                            "message_id": "",
                            "timestamp": datetime.now().isoformat(
                                timespec="seconds"
                            ),
                            "error": str(error)
                        })

                        self.log(
                            f"[!] {number}/{count} "
                            f"FAILED: {error}"
                        )

                    if number < count:
                        time.sleep(delay)

            self.save_report()

            self.set_progress(
                "Completed"
            )

            self.root.after(
                0,
                lambda: self.summary_label.config(
                    text=(
                        f"SENT: {sent}    "
                        f"FAILED: {failed}    "
                        f"TOTAL: {count}"
                    )
                )
            )

            self.log(
                "================================"
            )

            self.log(
                f"Completed: {sent}/{count} sent"
            )

            self.log(
                f"Failed: {failed}"
            )

            self.log(
                "Report saved in reports/"
            )

            self.log(
                "================================"
            )

            self.root.after(
                0,
                lambda: messagebox.showinfo(
                    "Completed",
                    f"Sent: {sent}\n"
                    f"Failed: {failed}\n"
                    f"Total: {count}\n\n"
                    f"Report saved in reports/"
                )
            )

        except smtplib.SMTPAuthenticationError:
            self.set_progress(
                "Authentication failed"
            )

            self.log(
                "[!] Gmail authentication failed."
            )

            self.root.after(
                0,
                lambda: messagebox.showerror(
                    "Authentication Error",
                    "Check Gmail address and "
                    "App Password in config.json."
                )
            )

        except Exception as error:
            self.set_progress(
                "Error"
            )

            self.log(
                f"[!] ERROR: {error}"
            )

            self.root.after(
                0,
                lambda: messagebox.showerror(
                    "Error",
                    str(error)
                )
            )

        finally:
            self.root.after(
                0,
                lambda: self.send_button.config(
                    state="normal"
                )
            )

    def save_report(self):
        os.makedirs(
            "reports",
            exist_ok=True
        )

        filename = (
            "reports/"
            "mail_report_"
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )

        fields = [
            "test_id",
            "mail_type",
            "number",
            "status",
            "message_id",
            "timestamp",
            "error"
        ]

        with open(
            filename,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=fields
            )

            writer.writeheader()

            for result in self.results:
                writer.writerow(result)


if __name__ == "__main__":
    root = tk.Tk()

    app = GmailTestSender(root)

    root.mainloop()