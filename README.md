# Ripple-Health
A DeFi medical payment and crowdfunding platform built on the XRP Ledger (XRPL)

## Description
Crowdfund & Connect is a decentralized finance (DeFi) healthcare payment platform built on the XRP Ledger. It enables direct doctor-to-patient billing, peer-to-peer payments, and built-in medical crowdfunding without relying on traditional financial methods.

The platform increases trust, transparency, and accessibility in healthcare payments using blockchain technology.

## Problems ?


## Features
- Direct Doctor-to-Patient Billing
    Verified doctors post treatment invoices on-chain.

    Each invoice includes:
    - Doctor wallet address
    - Patient wallet address
    - Service code
    - Amount
    - Timestamp

    Patients can instantly pay the invoice using XRP.

- Built-In Medical Crowdfunding
    If a patient cannot afford treatment:
    - The invoice becomes a public crowdfunding request.
    - Donors can:
    - View the verified doctor profile
    - See treatment type (without exposing sensitive data)
    - Contribute directly in XRP

    This removes fraud risk by ensuring all requests originate from verified doctors.

- Doctor Reserve Accounts (Liquidity Pool)
    Doctors can opt into a shared liquidity reserve pool.

    Example:
    - Patient treatment cost: $2,000
    - Crowdfunding raises: $1,400
    - Doctor reserve covers: $600 gap

    The system later repays the reserve from future donations.

    This ensures patients receive care immediately, even if crowdfunding is incomplete.

- Peer-to-Peer Payments 
    The platform uses the XRP Ledger for efficient, low-fee, borderless payments.

    Benefits:
    - No financial institution required to hold assets
    - Direct wallet-to-wallet transfers
    - Fast settlement
    - Low network fees

    This enables healthcare payments to function as easily as sending digital cash.


## How to Run
1. Backend: `cd backend`, create a virtualenv, `pip install -r requirements.txt`. Set optional env: `DATABASE_URI` (default `sqlite:///ripple_health.db`), `SECRET_KEY`, `ADMIN_EMAIL` (for verifying doctors and redacting invoices). Run `python app.py` (from `backend/` so `app.py` and imports resolve).
2. Frontend: open the HTML files in `frontend/` or serve them with any static server. Point API calls to the backend (e.g. `http://127.0.0.1:5000/api`). 

## Technologies Used
- HTML
- CSS
- JavaScript 
- Python
- XRPL (Blockchain)
- XRP (Cryptocurrency)
- DeFi
