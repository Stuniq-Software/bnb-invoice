from util import Database, RedisSession, get_booking_from_id, get_payment_from_id, get_stay_from_id, get_user_from_id, get_invoice_markdown_str, supabase_client
from typing import AnyStr, Optional, Tuple
from pathlib import Path
from uuid import uuid4
from pyppeteer import launch



class InvoiceRepository:
    db_session: Database
    redis_session: RedisSession

    def __init__(self, db_session: Database, redis_session: RedisSession):
        self.db_session = db_session
        self.redis_session = redis_session

    def _get_invoice_db(self, booking_id: str) -> Optional[str]:
        query = "SELECT invoice_url FROM invoices WHERE booking_id = %s"
        success, err = self.db_session.execute_query(query, (booking_id,))
        if not success:
            return None
        url = self.db_session.get_cursor().fetchone()
        if not url:
            return None
        return url[0]

    def get_invoice(self, booking_id: str) -> Optional[dict]:
        invoice = self.redis_session.get(booking_id)
        if invoice is None:
            invoice = self._get_invoice_db(booking_id)
            if not invoice:
                return None
            self.redis_session.set(booking_id, invoice, 120)
        return {"invoice_url": invoice}
    
    def upload_invoice(self, invoice_id: AnyStr, file: Path) -> Optional[str]:
        resp = supabase_client.storage.from_('invoices').upload(f"{invoice_id}.pdf", file, file_options={"content-type": "application/pdf"})
        if resp.is_error:
            return None
        url = supabase_client.storage.from_('invoices').get_public_url(f"{invoice_id}.pdf")
        return url

    async def generate_invoice(self, booking_id: str, payment_id: str) -> Tuple[bool, Optional[dict]]:
        booking = get_booking_from_id(booking_id)

        check = self.get_invoice(booking_id)
        if check:
            return False, "Invoice already exists!"
        
        payment = get_payment_from_id(payment_id)
        stay = get_stay_from_id(booking["stay_id"])

        user_query = "SELECT first_name, last_name, email, phone, line1, line2, city, state, country, postal_code FROM users JOIN address a on users.address_id = a.id WHERE users.id = %s"
        success, err = self.db_session.execute_query(user_query, (booking["user_id"],))
        if not success:
            raise Exception(err)
        user = self.db_session.get_cursor().fetchone()

        customer_name = f"{user[0]} {user[1]}"
        stay_name = stay["name"]
        ppn = stay["price_per_night"]
        nights = booking["nights"]
        currency = payment["currency"]
        amount_paid = payment["amount"]
        check_in = booking["checkin_date"]
        check_out = booking["checkout_date"] # Due date = checkout date

        stay_address = stay["address"]
        stay_address['stay_line1'] = stay_address.pop('line1')
        stay_address['stay_line2'] = stay_address.pop('line2')
        stay_address['stay_city'] = stay_address.pop('city')
        stay_address['stay_state'] = stay_address.pop('state')
        stay_address['stay_postal_code'] = stay_address.pop('country')
        stay_address['stay_country'] = stay_address.pop('postal_code') # Temporary fix
        email = user[2]
        phone = user[3]
        user_address = user[4:]

        invoice_id = str(uuid4())
        invoice = Path(f"./{invoice_id}.pdf")

        invoice_str = get_invoice_markdown_str(
            invoice_id,
            check_in,
            check_out,
            customer_name,
            stay_name,
            ppn,
            nights,
            currency,
            amount_paid,
            email,
            phone,
            *user_address,
            **stay_address
        )

        browser = await launch(headless=True)
        page = await browser.newPage()
        await page.setContent(invoice_str)
        await page.pdf({'path': invoice, 'format': 'A4'})
        await browser.close()

        
        print(f"Generated invoice: {invoice_id}")
        url = self.upload_invoice(invoice_id, invoice)
        if not url:
            return False, "Unable to Upload"
        invoice.unlink(missing_ok=True)

        query = "INSERT INTO invoices (id, booking_id, payment_id, invoice_url, amount, currency) VALUES (%s, %s, %s, %s, %s, %s)"
        success, err = self.db_session.execute_query(query, (invoice_id, booking_id, payment_id, url, amount_paid, currency))
        if not success:
            self.db_session.rollback()
            return False, str(err)
        self.db_session.commit()
        return True, {"invoice_id": invoice_id, "url": url}

    def create_and_upload_invoice(self, data: dict) -> Optional[AnyStr]:
        invoice = self.generate_invoice(data)
        invoice_url = self.upload_invoice(data["invoice_id"], invoice)
        return invoice_url if invoice_url else None
