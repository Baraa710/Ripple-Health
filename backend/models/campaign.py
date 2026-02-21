class Campaign:
    """
    Represents a health campaign with its details.
    Attributes:
    - campaign_id: Unique identifier for the campaign.
    - name: The name of the campaign.
    - doctor_address: The XRP Ledger account address of the doctor running the campaign.
    - description: A brief description of the campaign.
    - target_amount: Target amount in XRP drops.
    - current_amount: Current amount raised in XRP drops.
    - start_date: The start date of the campaign.
    - end_date: The end date of the campaign.
    - status: 'active', 'completed', or 'cancelled'.
    """
    def __init__(self, campaign_id: str, name: str, doctor_address: str, description: str, target_amount: int, start_date: str, end_date: str):
        self.campaign_id = campaign_id
        self.name = name
        self.doctor_address = doctor_address
        self.description = description
        self.target_amount = target_amount
        self.current_amount = 0
        self.start_date = start_date
        self.end_date = end_date
        self.status = 'active'

    def to_dict(self):
        return {
            'campaign_id': self.campaign_id,
            'name': self.name,
            'doctor_address': self.doctor_address,
            'description': self.description,
            'target_amount': self.target_amount,
            'current_amount': self.current_amount,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'status': self.status
        }

    def record_donation(self, amount: int):
        """
        Records a donation to the campaign.
        Updates the current amount and checks if the campaign is completed.
        """
        self.current_amount += amount
        if self.current_amount >= self.target_amount:
            self.status = 'completed'
    
    def goal_reached(self):
        """
        Checks if the campaign has reached its target amount.
        """
        return self.current_amount >= self.target_amount
    
    