from enum import Enum

class FeedbackType(Enum):
    SERVICE = "service"
    PROFESSIONAL = "professional"

class PaymentStatus(Enum):
    PENDING = "Pending"
    PAID = "Paid"
    FAILED = "Failed"
