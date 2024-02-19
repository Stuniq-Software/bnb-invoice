import requests
import os
from typing import Optional, AnyStr
from datetime import datetime
from string import Template
from pathlib import Path

BASE_PATH = Path(__file__).resolve().parent.parent




def get_stay_from_id(stay_id: AnyStr) -> Optional[dict]:
    response = requests.get(f"{os.getenv('STAY_SVC_URL')}/api/v1/stays/{stay_id}")
    if response.status_code == 200:
        return response.json()['data']
    else:
        return None


def get_user_from_id(user_id: AnyStr):
    # TODO: Implement this
    pass


def get_booking_from_id(booking_id: AnyStr) -> Optional[dict]:
    response = requests.get(f"{os.getenv('BOOKING_SVC_URL')}/api/v1/booking/{booking_id}?type=booking")
    if response.status_code == 200:
        return response.json()['data']
    else:
        return None


def get_payment_from_id(payment_id: AnyStr) -> Optional[dict]:
    response = requests.get(f"{os.getenv('PAYMENT_SVC_URL')}/api/v1/payments/status/{payment_id}")
    if response.status_code == 200:
        return response.json()['data']
    else:
        return None


def get_invoice_markdown_str(
        invoice_id: AnyStr,
        checkin_date: AnyStr,
        checkout_date: AnyStr,
        customer_name: AnyStr,
        stay_name: AnyStr,
        price_per_night: float,
        nights: int,
        currency: AnyStr,
        amount_paid: float,
        email: AnyStr,
        phone: AnyStr,
        line1: AnyStr,
        line2: AnyStr,
        city: AnyStr,
        state: AnyStr,
        country: AnyStr,
        postal_code: AnyStr,
        stay_line1: AnyStr,
        stay_line2: AnyStr,
        stay_city: AnyStr,
        stay_state: AnyStr,
        stay_country: AnyStr,
        stay_postal_code: AnyStr
) -> str:
    total = price_per_night * nights
    tax = round(total * 0.18, 2)
    grand_total = round(total + tax, 2)

    pdf_str = ""

    data = {
        "invoice_id": invoice_id.split("-")[-1],
        "checkin_date": checkin_date,
        "checkout_date": checkout_date,
        "customer_name": customer_name,
        "stay_name": stay_name,
        "price_per_night": price_per_night,
        "nights": nights,
        "currency": currency.upper(),
        "total": total,
        "tax": tax,
        "grand_total": grand_total,
        "amount_paid": amount_paid,
        "email": email,
        "phone": phone,
        "line1": line1,
        "line2": f", {line2}" if line2 else "",
        "city": city,
        "state": state,
        "country": country,
        "postal_code": postal_code,
        "stay_line1": stay_line1,
        "stay_line2": f", {stay_line2}" if stay_line2 else "",
        "stay_city": stay_city,
        "stay_state": stay_state,
        "stay_country": stay_country,
        "stay_postal_code": stay_postal_code,
        "date": datetime.now().strftime("%d-%m-%Y")
    }

    with open(BASE_PATH / "template" / "invoice.html") as html_template:
        template = Template(html_template.read())
        pdf_str = template.substitute(data)

    return pdf_str
