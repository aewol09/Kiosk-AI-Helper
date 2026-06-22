import time

class OrderManager:
    """
    Manages the state of the current order, the active kiosk step,
    and tracks user errors (mistakes) during the learning flow.
    """
    def __init__(self, brand="메가커피"):
        self.brand = brand
        self.current_step = 1  # Steps 1 to 6
        self.cart = []         # List of dicts: {'name': str, 'price': int, 'quantity': int, 'options': dict}
        self.pending_item = None # Item currently being configured in Step 2
        self.mistake_count = 0
        self.start_time = None
        self.end_time = None
        self.eat_in_option = None # '매장' or '포장'
        self.payment_method = None # '카드결제' or '쿠폰결제' etc.
        self.guide_target = "(ICE)아메리카노" # Default target menu for guidance

    def start_session(self):
        self.start_time = time.time()
        self.mistake_count = 0
        self.current_step = 1
        self.cart = []
        self.pending_item = None
        self.eat_in_option = None
        self.payment_method = None

    def end_session(self):
        self.end_time = time.time()

    def get_duration(self):
        if self.start_time and self.end_time:
            return int(self.end_time - self.start_time)
        elif self.start_time:
            return int(time.time() - self.start_time)
        return 0

    def add_mistake(self):
        self.mistake_count += 1

    def select_menu_to_configure(self, menu_name, price):
        """
        Sets the pending menu item and moves to Step 2 (Options).
        """
        self.pending_item = {
            'name': menu_name,
            'price': price,
            'quantity': 1,
            'options': {
                '텀블러': '사용 안함',
                '샷 추가': '기본(2샷)',
                '당도': '보통',
                '토핑': '없음'
            }
        }
        self.current_step = 2

    def update_pending_option(self, option_category, option_value, price_diff=0):
        """
        Updates an option for the pending item.
        """
        if self.pending_item:
            self.pending_item['options'][option_category] = option_value
            # In a real app, price_diff could adjust the price
            if price_diff > 0:
                self.pending_item['price'] += price_diff

    def commit_pending_item(self):
        """
        Adds the configured pending item to the cart and returns to Step 1.
        """
        if self.pending_item:
            # Check if item with same name and options already in cart
            found = False
            for item in self.cart:
                if item['name'] == self.pending_item['name'] and item['options'] == self.pending_item['options']:
                    item['quantity'] += 1
                    found = True
                    break
            if not found:
                self.cart.append(self.pending_item)
            self.pending_item = None
            self.current_step = 1

    def cancel_pending_item(self):
        """
        Cancels options selection and returns to Step 1.
        """
        self.pending_item = None
        self.current_step = 1

    def get_cart_total(self):
        total = 0
        for item in self.cart:
            total += item['price'] * item['quantity']
        return total

    def remove_item(self, index):
        if 0 <= index < len(self.cart):
            self.cart.pop(index)

    def set_eat_in(self, option):
        self.eat_in_option = option
        self.current_step = 5

    def set_payment_method(self, method):
        self.payment_method = method
        self.current_step = 6
