CREATE TABLE IF NOT EXISTS invoices (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_id uuid NOT NULL REFERENCES bookings(id),
    payment_id uuid NOT NULL REFERENCES payments(id),
    invoice_url text NOT NULL,
    amount numeric(10, 2) NOT NULL,
    currency text NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);