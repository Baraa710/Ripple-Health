import xrpl
from xrpl.wallet import Wallet, generate_faucet_wallet
from xrpl.clients import JsonRpcClient
from xrpl.models.transactions import Payment
from xrpl.transaction import submit_and_wait
from xrpl.models.requests import AccountInfo

# Connect to testnet
TESTNET_URL = "https://s.altnet.rippletest.net:51234/"
client = JsonRpcClient(TESTNET_URL)

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