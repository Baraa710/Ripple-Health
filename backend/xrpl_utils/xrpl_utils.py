import xrpl
from binascii import unhexlify
from xrpl.wallet import Wallet, generate_faucet_wallet
from xrpl.clients import JsonRpcClient
from xrpl.models.transactions import Payment, CredentialCreate, CredentialDelete
from xrpl.models.transactions.credential_accept import CredentialAccept
from xrpl.transaction import submit_and_wait
from xrpl.models.requests import AccountInfo, AccountObjects, AccountObjectType
from xrpl.utils import str_to_hex

TESTNET_URL = "https://s.altnet.rippletest.net:51234/"
client = JsonRpcClient(TESTNET_URL)

CREDENTIAL_TYPE = "VerifiedDoctor"
CREDENTIAL_TYPE_HEX = str_to_hex(CREDENTIAL_TYPE)

def create_account():
    """
    Creates a new XRP Ledger account and funds it on testnet.
    Returns the wallet object with account details.
    """
    wallet = Wallet.create()
    print(f"New account created: {wallet.address}")
    print(f"Seed: {wallet.seed}")
    
    # Fund the account on testnet (only works on testnet)
    # You'll need to use the XRP Ledger faucet or call this manually
    return wallet

def get_account_info(address: str):
    """
    Retrieves account information from the XRP Ledger.
    """
    try:
        request = AccountInfo(account=address, ledger_index="validated")  # Use model instead of dict
        account_info = client.request(request)
        return account_info.result
    except Exception as e:
        print(f"Error fetching account info: {e}")
        return None

def send_payment(sender_seed: str, recipient_address: str, amount: str):
    """
    Sends XRP payment from sender to recipient.
    amount: in XRP (will be converted to drops internally)
    """
    try:
        sender_wallet = Wallet.from_seed(sender_seed)
        
        payment = Payment(
            account=sender_wallet.address,
            destination=recipient_address,
            amount=str(int(float(amount) * 1_000_000))  # Convert XRP to drops
        )
        
        response = submit_and_wait(payment, client, sender_wallet)
        if response and response.result and "hash" in response.result:
            return response.result["hash"]
        return None
    except Exception as e:
        print(f"Error sending payment: {e}")
        return None


def fund_account_from_faucet(seed: str):
    """
    Fund an existing account (by seed) using the XRPL testnet faucet.
    Returns (success: bool, message: str).
    """
    try:
        wallet = Wallet.from_seed(seed)
        generate_faucet_wallet(client, wallet=wallet, debug=False)
        return True, "Account funded successfully"
    except Exception as e:
        return False, str(e)


# ---------------------------------------------------------------------------
# XRPL Credentials (on-chain doctor verification)
# ---------------------------------------------------------------------------

LSF_ACCEPTED = 0x00010000


def _credential_exists_on_chain(doctor_address: str, issuer_address: str):
    """Quick check if any credential (accepted or not) exists for this doctor from this issuer."""
    try:
        response = client.request(AccountObjects(
            account=doctor_address,
            type=AccountObjectType.CREDENTIAL,
        ))
        for obj in response.result.get("account_objects", []):
            if obj.get("Issuer") == issuer_address:
                cred_hex = obj.get("CredentialType", "")
                try:
                    if unhexlify(cred_hex).decode("ascii") == CREDENTIAL_TYPE:
                        return True
                except Exception:
                    continue
    except Exception:
        pass
    return False


def issue_credential(issuer_seed: str, doctor_address: str):
    """Issue a VerifiedDoctor credential on-chain. Returns (success, tx_hash_or_error)."""
    try:
        issuer_wallet = Wallet.from_seed(issuer_seed)
        print(f"[CRED] Issuing credential from {issuer_wallet.address} to {doctor_address}")
        tx = CredentialCreate(
            account=issuer_wallet.address,
            subject=doctor_address,
            credential_type=CREDENTIAL_TYPE_HEX,
        )
        response = submit_and_wait(tx, client=client, wallet=issuer_wallet, autofill=True)
        result = response.result
        result_code = result.get("engine_result", result.get("status", ""))
        if result_code == "tesSUCCESS":
            return True, result.get("hash", "")
        if _credential_exists_on_chain(doctor_address, issuer_wallet.address):
            print("[CRED] Ambiguous result but credential exists on-chain — treating as success")
            return True, "confirmed_on_chain"
        msg = result.get("engine_result_message", result_code)
        return False, msg or f"Unknown failure: {result_code}"
    except Exception as e:
        err = str(e)
        if "tecDUPLICATE" in err:
            print("[CRED] Credential already exists on-chain (tecDUPLICATE)")
            return True, "already_exists"
        issuer_wallet = Wallet.from_seed(issuer_seed)
        if _credential_exists_on_chain(doctor_address, issuer_wallet.address):
            print("[CRED] Exception thrown but credential exists on-chain — treating as success")
            return True, "confirmed_on_chain"
        import traceback
        traceback.print_exc()
        return False, f"{type(e).__name__}: {e}"


def accept_credential(doctor_seed: str, issuer_address: str):
    """Doctor accepts the pending VerifiedDoctor credential. Returns (success, tx_hash_or_error)."""
    try:
        doctor_wallet = Wallet.from_seed(doctor_seed)
        print(f"[CRED] Accepting credential for {doctor_wallet.address} from issuer {issuer_address}")
        tx = CredentialAccept(
            account=doctor_wallet.address,
            issuer=issuer_address,
            credential_type=CREDENTIAL_TYPE_HEX,
        )
        response = submit_and_wait(tx, client=client, wallet=doctor_wallet, autofill=True)
        result_code = response.result.get("engine_result", "")
        if result_code == "tesSUCCESS":
            return True, response.result.get("hash", "")
        if check_credential(doctor_wallet.address, issuer_address):
            print("[CRED] Ambiguous result but credential accepted on-chain — treating as success")
            return True, "confirmed_on_chain"
        msg = response.result.get("engine_result_message", result_code)
        return False, msg or result_code
    except Exception as e:
        err = str(e)
        if "tecDUPLICATE" in err:
            print("[CRED] Credential already accepted (tecDUPLICATE)")
            return True, "already_accepted"
        doctor_address = Wallet.from_seed(doctor_seed).address
        if check_credential(doctor_address, issuer_address):
            print("[CRED] Exception thrown but credential accepted on-chain — treating as success")
            return True, "confirmed_on_chain"
        import traceback
        traceback.print_exc()
        return False, f"{type(e).__name__}: {e}"


def check_credential(doctor_address: str, issuer_address: str):
    """Check if a doctor has an accepted VerifiedDoctor credential on-chain."""
    try:
        marker = None
        while True:
            response = client.request(AccountObjects(
                account=doctor_address,
                type=AccountObjectType.CREDENTIAL,
                marker=marker,
            ))
            if response.status != "success":
                return False

            for obj in response.result.get("account_objects", []):
                if obj.get("Issuer") != issuer_address:
                    continue
                if not (obj.get("Flags", 0) & LSF_ACCEPTED):
                    continue
                cred_type_hex = obj.get("CredentialType", "")
                try:
                    cred_type = unhexlify(cred_type_hex).decode("ascii")
                except Exception:
                    continue
                if cred_type == CREDENTIAL_TYPE:
                    return True

            marker = response.result.get("marker")
            if not marker:
                break
        return False
    except Exception:
        return False


def revoke_credential(issuer_seed: str, doctor_address: str):
    """Revoke (delete) a VerifiedDoctor credential on-chain. Returns (success, msg)."""
    try:
        issuer_wallet = Wallet.from_seed(issuer_seed)
        tx = CredentialDelete(
            account=issuer_wallet.address,
            subject=doctor_address,
            credential_type=CREDENTIAL_TYPE_HEX,
        )
        response = submit_and_wait(tx, client=client, wallet=issuer_wallet, autofill=True)
        result_code = response.result.get("engine_result", "")
        if result_code == "tesSUCCESS":
            return True, "Credential revoked"
        return False, result_code
    except Exception as e:
        return False, str(e)