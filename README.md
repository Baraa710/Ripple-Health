# CrowdCare

A DeFi medical payment and crowdfunding platform built on the XRP Ledger (XRPL)

## Inspiration

Access to healthcare remains a major global challenge, especially for people facing financial barriers or lack of insurance. Many delay treatment because they cannot afford upfront costs. Meanwhile, donors who want to help hesitate because they cannot verify whether medical fundraisers are legitimate. We set out to build a platform that uses blockchain to increase transparency, reduce financial barriers, and build verifiable trust in healthcare payments.

## What it does

CrowdCare is a decentralized healthcare payment and crowdfunding platform built on the XRP Ledger. Verified doctors post medical invoices, and patients can pay instantly using XRP or enable crowdfunding to receive donor support. Doctors are verified on-chain using XRPL's native Credentials amendment — anyone can confirm a doctor's legitimacy by querying the public ledger. Donors contribute knowing charges come from cryptographically verified providers. A crawlback mechanism allows suspicious invoices to be reported and redacted, preventing further payments to bad actors.

## How we built it

We used Flask for the backend API, HTML/CSS/JavaScript for the frontend, and SQLAlchemy with SQLite for data management. The platform supports three user roles — doctors, patients, and donors — each with dedicated dashboards. All payments use real wallet-to-wallet XRP transfers on the testnet via the `xrpl-py` library. For verification, when an admin verifies a doctor, the platform issues a `CredentialCreate` transaction on-chain. The doctor accepts it via `CredentialAccept`, and campaigns display an "On-Chain Verified" badge once confirmed.

## Challenges we ran into

Our biggest challenge was handling ambiguous responses from XRPL's `submit_and_wait` function. Credential transactions would succeed on the ledger, but the library would return empty results or throw exceptions before confirming the outcome — causing the UI to report failure despite on-chain success. We solved this with a ledger-query fallback: when responses are ambiguous, we query `AccountObjects` to verify the credential's actual on-chain state and report accordingly.

## Accomplishments that we're proud of

We built a fully functional prototype demonstrating the complete flow: doctors create invoices, patients pay or crowdfund, donors contribute — all with real XRP transactions. We're especially proud of integrating XRPL Credentials for on-chain doctor verification, making trust genuinely decentralized rather than locked in a database. The crawlback mechanism and doctor reserve accounts add practical safeguards for real-world healthcare crowdfunding.

## What we learned

We learned how to work with blockchain transactions and handle distributed system realities — "transaction submitted" doesn't always mean "confirmation received." We built resilient systems that verify on-chain state rather than trusting API responses. We also gained experience designing role-based platforms and applying XRPL's native features to real accessibility challenges.

## What's next for CrowdCare

We plan to integrate **XRPL Escrow** to hold crowdfunding contributions until campaign goals are met, with automatic refunds if they aren't. **XRPL Checks** would enable non-custodial refunds when fraudulent invoices are redacted. **XRPL DIDs** would give users portable, verifiable on-chain identities. Long term, we aim to pilot with clinics and scale globally as infrastructure for transparent, accessible healthcare payments.

## Features
- **On-Chain Doctor Verification (XRPL Credentials)**
    Doctors are verified using XRPL's native Credentials amendment. When an admin verifies a doctor, the platform issues a `VerifiedDoctor` credential on-chain via `CredentialCreate`. The doctor then accepts it via `CredentialAccept`, making their verification publicly visible on the ledger. Campaigns and invoices display an "On-Chain Verified" badge when the credential is accepted. Credentials can also be revoked on-chain via `CredentialDelete`.

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
| `ISSUER_SEED` | *(none)* | XRPL seed for the platform's credential issuer account (on-chain doctor verification) |

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
| PUT | `/api/users/<id>/verify` | Admin | Verify a doctor (+ issue on-chain credential) |
| PUT | `/api/users/<id>/revoke` | Admin | Revoke doctor verification (+ revoke credential) |
| POST | `/api/credentials/accept` | Doctor | Accept pending on-chain credential |
| GET | `/api/credentials/status` | Yes | Check on-chain credential status |

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

## On-Chain Doctor Verification (XRPL Credentials)

CrowdCare uses XRPL's native **Credentials** amendment to verify doctors on-chain:

1. **Admin verifies a doctor** (`PUT /api/users/<id>/verify`) — the platform's issuer account issues a `VerifiedDoctor` credential to the doctor's XRP address.
2. **Doctor accepts the credential** (`POST /api/credentials/accept`) — the credential is accepted on-chain and becomes visible to anyone querying the ledger.
3. **Campaigns show on-chain status** — if the issuing doctor's credential is accepted, campaigns display an "On-Chain Verified" badge.
4. **Revocation** (`PUT /api/users/<id>/revoke`) — the admin can revoke verification, which also deletes the credential from the ledger.

**Setup**: Set the `ISSUER_SEED` environment variable to a funded XRPL testnet account seed. The platform uses this account to issue and revoke credentials.

### Handling Ambiguous XRPL Responses

During development we encountered a recurring issue with `xrpl-py`'s `submit_and_wait` function: credential transactions (`CredentialCreate`, `CredentialAccept`) would succeed on the ledger but the function would either return an empty `engine_result` or throw an `XRPLReliableSubmissionException` before confirming the outcome. This caused the API to report failure even though the credential was actually written on-chain.

**Symptoms observed:**
- `submit_and_wait` returns a response with an empty `engine_result` — the transaction landed but the result field is missing
- `submit_and_wait` throws `XRPLReliableSubmissionException: Transaction failed: tecDUPLICATE` on a second attempt, proving the first attempt did succeed
- The UI shows "Failed to accept credential" but on page reload the credential appears as accepted

**How we solved it:**
Both `issue_credential` and `accept_credential` now use a **ledger-query fallback**. When the response is ambiguous (empty result code, exception, or non-`tesSUCCESS` code), the functions query the doctor's `AccountObjects` on-chain to check whether the credential actually exists and is accepted. If it does, the operation is reported as successful. This handles three cases:
1. **Normal return with empty `engine_result`** — falls back to ledger query
2. **`tecDUPLICATE` exception** — credential already exists, treated as success
3. **Other exceptions** — ledger query determines if the transaction landed despite the error

This pattern ensures the API never falsely reports failure when the on-chain state confirms success.

## Future Developments

### Escrow-Based Crowdfunding
Currently, crowdfunding contributions are sent directly to the doctor's wallet. A more secure approach would use [XRPL Escrow](https://xrpl.org/docs/concepts/payment-types/escrow) to hold funds until the campaign goal is met or a deadline passes. If the goal isn't reached, escrowed funds automatically return to donors — no trust required. This also strengthens the crawlback mechanism: if an invoice is reported as fraudulent while contributions are still in escrow, the escrow can be cancelled before funds are ever released to the doctor.

### Check-Based Crawlback Refunds
When a fraudulent invoice is redacted, there is currently no mechanism to recover funds already paid. [XRPL Checks](https://xrpl.org/docs/concepts/payment-types/checks) would allow the platform to require the doctor to issue a Check back to the patient or donors. The Check sits on-chain until the recipient is ready to cash it, providing a non-custodial refund path that doesn't require the doctor and recipient to be online at the same time.

### Decentralized Identity (DID)
Doctor and patient identities currently live only in the SQLite database. [XRPL DID](https://xrpl.org/docs/concepts/accounts/decentralized-identifiers) would allow each user to have a verifiable, portable on-chain identity tied to their XRP account. A doctor's verification status, credentials, and history could be queried directly from the ledger by any application — not just this platform. This moves trust from a single database to the decentralized ledger, enabling interoperability with other healthcare or identity systems.

## Technologies Used
- **Frontend**: HTML, CSS, JavaScript (vanilla fetch API)
- **Backend**: Python, Flask, Flask-Login, SQLAlchemy, SQLite
- **Blockchain**: XRPL (XRP Ledger), xrpl-py library, XRPL Credentials
- **Network**: XRPL Testnet
