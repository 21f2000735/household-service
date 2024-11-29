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


from enum import Enum

class ServiceType(Enum):
    PLUMBING = (1, "Plumber", 500.0, "image/plumbing.png", "Fix leaks, clogs, and pipe issues. Ensure your plumbing system is working efficiently with our expert services.")
    ELECTRICAL = (2, "Electrician", 500.0, "image/electrician.png", "Install and repair electrical systems. Handle electrical wiring, outlets, and circuit breakers with safety and professionalism.")
    CLEANING = (3, "Cleaner", 300.0, "image/cleaning.png", "Thorough home and office cleaning services. We offer deep cleaning for homes, carpets, and commercial spaces.")
    GARDENING = (4, "Gardener", 300.0, "image/gardening.png", "Maintain your garden with care. Offering services like lawn care, hedge trimming, plant care, and garden design.")

    def __init__(self, id, display_name, base_price, image_url, description):
        self.id = id
        self.display_name = display_name
        self.base_price = base_price
        self.image_url = image_url
        self.description = description

    @classmethod
    def get_by_id(cls, id):
        for service_type in cls:
            if service_type.id == id:
                return service_type
        return None

    @classmethod
    def list_all(cls):
        return list(cls)

