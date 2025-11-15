import math
import pathlib

class Coupon:
    min_total_amount = 0.0  # Minimum amount to apply the coupon
    discount = 0.0          # Discount amount
    codes = []              # List of coupon codes
    def __init__(self, codes: str | list[str], min_total_amount:float, discount: float):
        """
        Initialize a Coupon instance.
        Args:
            codes (str | list[str]): The coupon code(s). Can be a single code string or a list of codes.
            min_total_amount (float): The minimum total amount required to apply the coupon.
            discount (float): The discount percentage to be applied.
        """
        # Convert single code string to list for uniform handling
        if isinstance(codes, str):
            self.codes = codes.split(",",)  # Support comma-separated codes in a single string
        elif isinstance(codes, list):
            self.codes = codes 
        elif not self.codes or all(code.strip() == "" for code in self.codes):
            raise ValueError("At least one non-empty coupon code must be provided.")
        else:
            raise ValueError("Codes must be a string or a list of strings.")
        
        self.min_total_amount = min_total_amount
        self.discount = discount

        if self.get_percentage_discount() > 1.0:
            raise ValueError("Discount percentage cannot be greater than 100% of the minimum total amount.")

    def is_applicable(self, total_amount: float) -> bool:
        """Check if the coupon can be applied to the given total amount.
        Args:
            total_amount (float): The total amount of the order.
        Returns:
            bool: True if the coupon can be applied, False otherwise.
        """
        return total_amount >= self.min_total_amount

    def apply_discount(self, total_amount: float) -> float:
        """Apply the discount to the given total amount.
        Args:
            total_amount (float): The total amount of the order.
        Returns:
            float: The total amount after applying the discount.
        """
        return total_amount * (1 - self.discount / 100)
    
    def get_percentage_discount(self) -> float:
        """
        Get the percentage discount offered by the coupon.
        Returns:
            float: The percentage discount, as value from 1.0 to 0.0.
        """
        return self.discount / self.min_total_amount

    def __str__(self):
        """String representation of the Coupon instance."""
        codes_str = ", ".join(self.codes)
        return f"Coupon(codes=[{codes_str}], min_total_amount={self.min_total_amount}, discount={self.discount}%)"

class CartItem:
    # implemet params:
    # Item Name	Variant/Option	Current Price (USD)	Qty	Original Price (USD)	Savings (USD)	Shipping (USD)	Store	Stock Note
    name_variant = ""
    current_price = 0.0
    quantity = 0
    original_price = 0.0
    savings = 0.0
    shipping = 0.0
    store = ""
    stock_note = ""

    def __init__(self, **kwargs):
        """
        Initialize a CartItem instance.
        Args:
            kwargs: Keyword arguments for initializing the CartItem.
            name (str): The name of the item.
            variant (str): The variant or option of the item.
            current_price (float): The current price of the item.
            quantity (int): The quantity of the item.
            original_price (float): The original price of the item.
            savings (float): The savings on the item.
            shipping (float): The shipping cost for the item.
            store (str): The store from which the item is purchased.
            stock_note (str): Any stock notes for the item.
        Returns:
            None
        """
        self.name = kwargs.get("name", "")
        self.variant = kwargs.get("variant", "")
        self.price = float(kwargs.get("current_price", 0.0))
        self.quantity = int(kwargs.get("quantity", 0))
        self.original_price = float(kwargs.get("original_price", 0.0))
        self.savings = float(kwargs.get("savings", 0.0))
        self.shipping = float(kwargs.get("shipping", 0.0))
        self.store = kwargs.get("store", "")
        self.stock_note = kwargs.get("stock_note", "")
        if self.name == "":
            raise ValueError("Item name cannot be empty")
        if self.variant == "":
            raise ValueError("Item variant cannot be empty.")
        if self.price < 0:
            raise ValueError("Price cannot be negative.")
        if self.quantity < 0:
            raise ValueError("Quantity cannot be negative.")
        if self.original_price < 0:
            raise ValueError("Original price cannot be negative.")
        if self.savings < 0:
            raise ValueError("Savings cannot be negative.")
        if self.savings > self.original_price:
            raise ValueError("Savings cannot be greater than original price.")
        if self.savings > (self.original_price - self.price):
            raise ValueError("Savings cannot be greater than the difference between original price and current price.")
        
    def get_total_price(self) -> float:
        """Calculate the total price for this cart item.
        Returns:
            float: The total price for this cart item.
        """
        return self.price * self.quantity

    def __str__(self):
        """String representation of the CartItem instance."""
        return f"CartItem(name={self.name}, price={self.price}, quantity={self.quantity})"
    

COUPONS_FILE_PATH = "coupons.txt"
CART_FILE_PATH = "cart.txt"

def load_cart_items_from_file(cart_file_path: str) -> list[CartItem]:
    pass

def load_coupons_from_file(coupons_file_path: str) -> list[Coupon]:
    pass

def generate_coupon_combinations(coupons: list[Coupon]) -> list[tuple[Coupon]]:
    pass

def main():
    my_cart = load_cart_items_from_file(CART_FILE_PATH)
    available_coupons = load_coupons_from_file(COUPONS_FILE_PATH)
    total_amount = sum(item.get_total_price() for item in my_cart)

    if not available_coupons:
        print("No available coupons.")
        return
    
    if not my_cart:
        print("Cart is empty.")
        return
    
    if total_amount < any(coupon.min_total_amount for coupon in available_coupons):
        print("Total amount is less than the minimum required for any coupon.")
        return

    #list of applicable coupons
    applicable_coupons = [coupon for coupon in available_coupons if coupon.is_applicable(total_amount)]

    #list of applicable coupons PAIRS
    applicable_coupon_pairs = [(c1, c2) for i, c1 in enumerate(available_coupons) for c2 in available_coupons[i+1:] if c1.is_applicable(total_amount) and c2.is_applicable(total_amount)]
    # todo - check is AI suggested best coupon logic is correct

    #max coupons to reach the total amount (worst case scenario):
    max_coupons_needed:int = 0
    total_discounted:float = 0.0
    for discount in [coupon.discount for coupon in available_coupons].sort(): #sort discounts ascending
        max_coupons_needed += 1
        total_discounted += discount
        if total_discounted >= total_amount:
            break

    coupon_combo_range = range(1, max_coupons_needed + 1)

    for counpon_count in coupon_combo_range:
        pass

    




    max_coupons_needed = math.ceil(total_amount / min(coupon.min_total_amount for coupon in available_coupons))
    


if __name__ == "__main__":
    main()