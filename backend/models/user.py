from xrpl_utils.xrpl_utils import create_account, get_account_info, send_payment
class User:
    def __init__(self, user_id, name, email, user_type):
        """
        user_type: 'doctor' or 'patient' or 'donor'
        account_address: XRP Ledger account address
        """
        self.user_id = user_id
        self.name = name
        self.email = email
        self.wallet = create_account()
        self.account_address = self.wallet.address
        self.user_type = user_type
        self.created_at = None
        
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email,
            'account_address': self.account_address,
            'user_type': self.user_type,
            'created_at': self.created_at
        }

