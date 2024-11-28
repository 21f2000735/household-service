from enum import Enum

class FeedbackType(Enum):
    SERVICE = "service"
    PROFESSIONAL = "professional"


class PaymentStatus(Enum):
    PENDING = "Pending"
    PAID = "Paid"
    FAILED = "Failed"

from enum import Enum

class ServiceType(Enum):
    PLUMBING = (1, "Plumbing", 500.0, "image/plumbing.png")
    ELECTRICAL = (2, "Electrical", 700.0, "image/electrician.png")
    CLEANING = (3, "Cleaning", 300.0, "image/cleaning.png")
    GARDENING = (4, "Gardening", 400.0, "image/gardening.png")
    # You can uncomment the other service types when required
    # OTHER = (5, "Others", 0.0, "image/other.png")


    def __init__(self, id, display_name, base_price, image_url):
        self.id = id  # Unique identifier for the service
        self.display_name = display_name  # Human-readable name
        self.base_price = base_price  # Default price for the service
        self.image_url = image_url  # Image URL for the service

    @classmethod
    def get_by_id(cls, id):
        for service_type in cls:
            if service_type.id == id:
                return service_type
        return cls.OTHER

    @classmethod
    def list_all(cls):
        return [service_type for service_type in cls]
