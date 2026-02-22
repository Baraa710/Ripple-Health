# Ripple-Health
A DeFi medical payment and crowdfunding platform built on the XRP Ledger (XRPL)

## Description
Crowdfund & Connect is a decentralized finance (DeFi) healthcare payment platform built on the XRP Ledger. It enables direct doctor-to-patient billing, peer-to-peer payments, and built-in medical crowdfunding without relying on traditional financial methods.

The platform increases trust, transparency, and accessibility in healthcare payments using blockchain technology.

## Features
- **Direct Doctor-to-Patient Billing**
    Verified doctors post treatment invoices on-chain. Each invoice includes doctor ID, patient ID, amount, treatment description, and timestamp. Patients can instantly pay the invoice using XRP.

- **Built-In Medical Crowdfunding**
    If a patient cannot afford treatment, they can enable crowdfunding on their invoice. The invoice becomes a public campaign where donors can view the verified doctor profile, see the treatment type, and contribute directly in XRP. This removes fraud risk by ensuring all requests originate from verified doctors.

- **Doctor Reserve Accounts**
    Doctors can maintain a reserve account balance. If crowdfunding falls short, the doctor can cover the gap from their reserve to ensure the patient receives care immediately.

- **Crawlback (Fraud Protection)**
    Any user can report a suspicious invoice. Admins can redact fraudulent invoices, preventing further payments. This protects donors and patients from bad actors.

- **Peer-to-Peer Payments**
    All payments settle on the XRP Ledger -- no financial institution required. Direct wallet-to-wallet transfers with fast settlement and low network fees.

## Project Structure
```
Ripple-Health/
├── backend/
│   ├── app.py                  # Flask app entry point
│   ├── extensions.py           # SQLAlchemy db setup
│   ├── requirements.txt        # Python dependencies
│   ├── models/
│   │   ├── user.py             # User model (doctor, patient, donor)
│   │   ├── invoice.py          # Invoice model
│   │   ├── campaign.py         # Crowdfunding campaign model
│   │   └── reserve.py          # Doctor reserve account model
│   ├── routes/
│   │   ├── users.py            # Auth & user API (/api/register, /api/login, etc.)
│   │   ├── invoice.py          # Invoice API (/api/invoices/*)
│   │   ├── payment.py          # Payment API (/api/payments/*)
│   │   ├── campaign.py         # Campaign API (/api/campaigns/*)
│   │   ├── reserve.py          # Reserve API (/api/reserve/*)
│   │   └── pages.py            # Page routes (serves HTML templates)
│   └── xrpl_utils/
│       └── xrpl_utils.py       # XRPL wallet & payment helpers
├── templates/
│   ├── base.html               # Landing page
│   ├── campaigns.html          # Public campaigns listing
│   ├── patients/
│   │   ├── login.html          # Patient login
│   │   ├── signup.html         # Patient registration
│   │   └── dashboard.html      # Patient dashboard
│   ├── doctors/
│   │   ├── login.html          # Doctor login
│   │   ├── signup.html         # Doctor registration
│   │   └── dashboard.html      # Doctor dashboard
│   └── donors/
│       ├── login.html          # Donor login
│       ├── signup.html         # Donor registration
│       └── dashboard.html      # Donor dashboard
└── static/
    └── platform.css            # Stylesheet
```

## How to Run

### 1. Setup
```bash
cd Ripple-Health/backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

### 2. Environment Variables (optional)
| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | `dev-secret-change-in-production` | Flask session secret |
| `DATABASE_URI` | `sqlite:///ripple_health.db` | Database connection string |
| `ADMIN_EMAIL` | *(none)* | Email of admin user (can verify doctors & redact invoices) |

### 3. Run
```bash
python app.py
```
Open **http://127.0.0.1:5000** in your browser.

### 4. Test Flow
1. Go to `/doctors/signup` and register a doctor account
2. Go to `/patients/signup` and register a patient account
3. Log in as the doctor at `/doctors/login` → doctor dashboard
4. Fund your wallet (testnet faucet button)
5. Create an invoice for the patient (use patient's user ID)
6. Log out, log in as patient at `/patients/login` → patient dashboard
7. Fund wallet, then pay the invoice or enable crowdfunding
8. Log in as a donor to contribute to crowdfunding campaigns

## API Endpoints

### Auth & Users (`/api`)
| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/api/register` | No | Register (name, email, password, user_type) |
| POST | `/api/login` | No | Login (email, password) |
| POST | `/api/logout` | Yes | Logout |
| GET | `/api/me` | Yes | Current user info |
| POST | `/api/fund-me` | Yes | Fund wallet from testnet faucet |
| GET | `/api/users/<id>` | No | Get user by ID |
| GET | `/api/users/verified` | No | List verified doctors |
| PUT | `/api/users/<id>/verify` | Admin | Verify a doctor |

### Invoices (`/api/invoices`)
| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/invoices` | Yes | List current user's invoices |
| POST | `/api/invoices/create` | Doctor | Create invoice for a patient |
| GET | `/api/invoices/<id>` | Yes | View invoice details |
| PATCH | `/api/invoices/<id>` | Patient | Toggle crowdfunding |
| POST | `/api/invoices/<id>/report` | Yes | Report suspicious invoice |
| POST | `/api/invoices/<id>/redact` | Admin | Redact fraudulent invoice |

### Payments (`/api/payments`)
| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/api/payments/pay/<invoice_id>` | Yes | Pay an invoice in XRP |

### Reserve (`/api/reserve`)
| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/reserve/balance` | Doctor | Get reserve balance |
| POST | `/api/reserve/add` | Doctor | Add funds to reserve |
| POST | `/api/reserve/use-for-invoice/<id>` | Doctor | Cover invoice gap from reserve |

### Campaigns (`/api/campaigns`)
| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/campaigns` | No | List active campaigns |
| GET | `/api/campaigns/<id>` | No | Campaign details |

## Technologies Used
- **Frontend**: HTML, CSS, JavaScript (vanilla fetch API)
- **Backend**: Python, Flask, Flask-Login, SQLAlchemy, SQLite
- **Blockchain**: XRPL (XRP Ledger), xrpl-py library
- **Network**: XRPL Testnet
