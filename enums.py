from enum import Enum

class FeedbackType(Enum):
    SERVICE = "service"
    PROFESSIONAL = "professional"


class PaymentStatus(Enum):
    PENDING = "Pending"
    PAID = "Paid"
    FAILED = "Failed"

class ServiceType(Enum):
    PLUMBING = (1, "Plumbing", 500.0)
    ELECTRICAL = (2, "Electrical", 700.0)
    CLEANING = (3, "Cleaning", 300.0)
    GARDENING = (4, "Gardening", 400.0)
    OTHER = (5, "Others", 0.0)

    @classmethod
    def get_by_id(cls, id):
        for service_type in cls:
            if service_type.id == id:
                return service_type
        return cls.OTHER

    @classmethod
    def list_all(cls):
        return [service_type for service_type in cls]