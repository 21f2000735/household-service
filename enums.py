from enum import Enum

class FeedbackType(Enum):
    SERVICE = "service"
    PROFESSIONAL = "professional"


class PaymentStatus(Enum):
    PENDING = "Pending"
    PAID = "Paid"
    FAILED = "Failed"



class ServiceRequestStatus(Enum): #requested/assigned/closed
    REQUESTED = (1, "requested")
    ASSIGNED = (2, "assigned")
    CLOSED = (3, "closed")

    def __init__(self, id, display_name):
        self.id = id
        self.display_name = display_name

    @classmethod
    def get_by_id(cls, id):
        """
        Get the status by ID.
        Returns None if no matching ID is found.
        """
        return next((status for status in cls if status.id == id), None)

    @classmethod
    def list_all(cls):
        """
        List all statuses as a list.
        """
        return [status for status in cls]

    def __str__(self):
        """
        Return a string representation of the enum (for display purposes).
        """
        return self.display_name


class ServiceType(Enum):
    PLUMBING = (1, "Plumber", 500.0, "image/plumbing.png")
    ELECTRICAL = (2, "Electrician", 500.0, "image/electrician.png")
    CLEANING = (3, "Cleaner", 300.0, "image/cleaning.png")
    GARDENING = (4, "Gardener", 300.0, "image/gardening.png")


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
