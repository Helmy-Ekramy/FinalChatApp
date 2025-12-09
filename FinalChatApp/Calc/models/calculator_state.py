import uuid

class CalculatorState:
    def __init__(self):
        self.expression = ""
        self.result = "0"
        self.last_request_id = ""
        self.last_was_operator = False

    def add_number(self, number):
        """Add a number to the expression"""
        self.expression += str(number)
        self.last_was_operator = False

    def add_operator(self, operator):
        """Add an operator to the expression"""
        if not self.last_was_operator and self.expression:
            self.expression += operator
            self.last_was_operator = True

    def clear(self):
        """Clear the expression and result"""
        self.expression = ""
        self.result = "0"
        self.last_was_operator = False

    def generate_request_id(self):
        """Generate a new unique request ID"""
        self.last_request_id = str(uuid.uuid4())
        return self.last_request_id

    def is_latest_request(self, request_id):
        """Check if this is the latest request"""
        return request_id == self.last_request_id

    def can_add_operator(self):
        """Check if an operator can be added"""
        return not self.last_was_operator and len(self.expression) > 0
