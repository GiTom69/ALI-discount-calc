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
    """
    Load cart items from a text file containing AliExpress shopping cart data.
    
    Pattern for each item:
    - Stock note (e.g., "Only X left", "Almost sold out") - SKIP
    - URL line starting with <https://...> - SKIP
    - URL parameter lines (mp=..., pdp_npi=...) - SKIP
    - Product name (may span 1-2 lines, ends with <https://... on last line)
    - More URL lines - SKIP
    - Variant/Option line
    - Current price (US $X.XX)
    - Original price (US $X.XX) - optional
    - Savings line (Save US $X.XX or US $X.XX off since added) - optional
    - "Coupons applicable" - SKIP
    - Shipping line (Shipping: US $X.XX or Free shipping)
    - Store line (Store Name <https://...>)
    
    Args:
        cart_file_path (str): Path to the cart file.
        
    Returns:
        list[CartItem]: List of CartItem objects parsed from the file.
        
    Raises:
        FileNotFoundError: If the cart file doesn't exist.
        ValueError: If the file format is invalid or cannot be parsed.
    """
    import re
    
    cart_path = pathlib.Path(cart_file_path)
    if not cart_path.exists():
        raise FileNotFoundError(f"Cart file not found: {cart_file_path}")
    
    with open(cart_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find where cart starts (after "*Cart*" line)
    cart_start = content.find('*Cart*')
    if cart_start == -1:
        raise ValueError("Could not find cart section in file (missing '*Cart*' marker)")
    
    # Find where cart ends (at "Summary" section or end of file)
    cart_end = content.find('Summary', cart_start)
    if cart_end == -1:
        cart_end = len(content)
    
    cart_content = content[cart_start:cart_end]
    lines = cart_content.split('\n')
    
    cart_items = []
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines, stock notes, navigation markers
        if (not line or 
            line.startswith('*') or
            line.startswith('Only ') or
            line.startswith('Almost ') or
            line.startswith('Select all') or
            line.startswith('Delete selected') or
            line.startswith('Ends:') or
            line.startswith('Shipped by')):
            i += 1
            continue
        
        # Skip URL-only lines (start with http/www or contain only URL)
        if (line.startswith('http') or 
            line.startswith('www.') or
            line.startswith('<') or  # Catch <https://...
            line.startswith('mp=') or
            'pdp_npi=' in line or
            'disableNav=' in line):
            i += 1
            continue
        
        # Look for product name: substantial text that's not a price/metadata
        # Must be at least 20 chars, contain letters, and not be system text
        if (len(line) > 20 and 
            not line.startswith('US $') and
            'Store' not in line and
            'Shipping' not in line and
            'Coupons' not in line and
            'Sale' not in line[:10] and  # "Sale" might be in product name
            'Save US' not in line and
            any(c.isalpha() for c in line)):
            
            # This looks like a product name
            name_parts = []
            
            # Check if line has URL at the end
            if '<https://' in line:
                # Extract name part before URL
                name_part = line.split('<https://')[0].strip()
                if name_part:
                    name_parts.append(name_part)
                i += 1
                # Skip following URL lines
                while i < len(lines) and (lines[i].strip().startswith('www.') or 
                                          lines[i].strip().startswith('http') or
                                          lines[i].strip().startswith('mp=') or
                                          'pdp_npi=' in lines[i]):
                    i += 1
            else:
                # Name might span multiple lines - add first line
                name_parts.append(line)
                i += 1
                
                # Check next line for continuation
                if i < len(lines):
                    next_line = lines[i].strip()
                    # Keep adding lines until we hit a URL marker
                    if next_line and '<https://' in next_line:
                        # This line has continuation of name + URL
                        name_part = next_line.split('<https://')[0].strip()
                        if name_part:
                            name_parts.append(name_part)
                        i += 1
                        # Skip following URL lines
                        while i < len(lines) and (lines[i].strip().startswith('www.') or 
                                                  lines[i].strip().startswith('http') or
                                                  lines[i].strip().startswith('mp=') or
                                                  'pdp_npi=' in lines[i]):
                            i += 1
                    elif next_line and not next_line.startswith('US $'):
                        # Might be another line of the name (without URL yet)
                        # This handles cases where name is on multiple lines before URL
                        if len(next_line) > 20:  # Long line, probably name continuation
                            name_parts.append(next_line)
                            i += 1
                            # Now skip URL lines
                            while i < len(lines) and (lines[i].strip().startswith('www.') or 
                                                      lines[i].strip().startswith('http') or
                                                      lines[i].strip().startswith('<') or
                                                      lines[i].strip().startswith('mp=') or
                                                      'pdp_npi=' in lines[i]):
                                i += 1
            
            full_name = ' '.join(name_parts).strip()
            
            # Now parse the structured fields
            item_data = {'name': full_name}
            
            # Next line should be variant
            if i < len(lines):
                variant_line = lines[i].strip()
                # Variant should be text, not price, not URL, not system message
                # URLs typically have :// or start with www. or http
                is_url = (variant_line.startswith('www.') or 
                         variant_line.startswith('http') or
                         '://' in variant_line)
                
                if (variant_line and 
                    not variant_line.startswith('US $') and
                    not is_url and
                    not variant_line.startswith('mp=') and
                    'Coupons' not in variant_line and
                    'Shipping' not in variant_line and
                    'Sale' not in variant_line and
                    'Save' not in variant_line and
                    len(variant_line) < 100):  # Variants should be reasonably short
                    item_data['variant'] = variant_line
                    i += 1
            
            # Next line should be current price
            if i < len(lines) and lines[i].strip().startswith('US $'):
                price_match = re.search(r'US \$(\d+\.?\d*)', lines[i])
                if price_match:
                    item_data['current_price'] = price_match.group(1)
                    i += 1
            
            # Next might be original price (another US $ line)
            if i < len(lines) and lines[i].strip().startswith('US $'):
                price_match = re.search(r'US \$(\d+\.?\d*)', lines[i])
                if price_match:
                    item_data['original_price'] = price_match.group(1)
                    i += 1
            
            # Next might be savings or Sale line
            if i < len(lines):
                savings_line = lines[i].strip()
                if 'Save' in savings_line or 'off since added' in savings_line or 'Sale' in savings_line:
                    save_match = re.search(r'US \$(\d+\.?\d*)', savings_line)
                    if save_match:
                        item_data['savings'] = save_match.group(1)
                    i += 1
            
            # Skip "Coupons applicable" line
            if i < len(lines) and 'Coupons' in lines[i]:
                i += 1
            
            # Next should be shipping
            if i < len(lines) and ('Shipping' in lines[i] or 'Free shipping' in lines[i]):
                shipping_line = lines[i].strip()
                if 'Free shipping' in shipping_line:
                    item_data['shipping'] = '0.0'
                else:
                    ship_match = re.search(r'US \$(\d+\.?\d*)', shipping_line)
                    if ship_match:
                        item_data['shipping'] = ship_match.group(1)
                i += 1
            
            # Next should be store
            if i < len(lines):
                store_line = lines[i].strip()
                if 'Store' in store_line:
                    # Extract store name (text before <https://>)
                    if '<https://' in store_line:
                        store_name = store_line.split('<https://')[0].strip()
                    else:
                        store_name = store_line
                    item_data['store'] = store_name
                    i += 1
            
            # Validate and create item
            if ('variant' in item_data and 
                'current_price' in item_data and 
                'store' in item_data):
                
                # Set defaults
                if 'original_price' not in item_data:
                    item_data['original_price'] = item_data['current_price']
                if 'savings' not in item_data:
                    item_data['savings'] = '0.0'
                if 'shipping' not in item_data:
                    item_data['shipping'] = '0.0'
                
                item_data['quantity'] = 1
                item_data['stock_note'] = ''
                
                try:
                    cart_item = CartItem(**item_data)
                    cart_items.append(cart_item)
                except ValueError:
                    # Skip items that fail validation
                    pass
            
            continue
        
        i += 1
    
    if not cart_items:
        raise ValueError("No valid cart items found in file. Please check the file format.")
    
    return cart_items

def load_coupons_from_file(coupons_file_path: str) -> list[Coupon]:
    pass

def generate_coupon_combinations(coupons: list[Coupon]) -> list[tuple[Coupon]]:
    pass

def main():
    my_cart = load_cart_items_from_file(CART_FILE_PATH)
    if not my_cart:
        print("Cart is empty.")
        return
    
    available_coupons = load_coupons_from_file(COUPONS_FILE_PATH)
    if not available_coupons:
        print("No available coupons.")
        return
    
    total_amount = sum(item.get_total_price() for item in my_cart)
    if total_amount < any(coupon.min_total_amount for coupon in available_coupons):
        print("Total amount is less than the minimum required for any coupon.")
        return
    


    #list of applicable coupons
    applicable_coupons = [coupon for coupon in available_coupons if coupon.is_applicable(total_amount)]

    #list of applicable coupons PAIRS
    applicable_coupon_pairs = [(c1, c2) for i, c1 in enumerate(available_coupons) for c2 in available_coupons[i+1:] if c1.is_applicable(total_amount) and c2.is_applicable(total_amount)]
    # todo - check is AI suggested best coupon logic is correct

    #max coupons to reach the total amount (worst case scenario, from smallest coupon be ascending price):
    max_coupons_needed:int = 0
    total_discounted:float = 0.0
    for discount in [coupon.discount for coupon in available_coupons].sort(): #sort discounts ascending
        max_coupons_needed += 1
        total_discounted += discount
        if total_discounted >= total_amount:
            break

    coupon_count_combo_range = range(1, max_coupons_needed + 1)
    coupon_groups = list[list[Coupon]]      # use this simple data structure and calculate the tot price on the fly


    for counpon_count in coupon_count_combo_range:
        # todo - generate all the coupon variations,
        # assume evry coupon can be used as many time as three are coupon codes

        # for each counpon_count:
        # create a list <coupon_groups> of coupon combinations with a total price for each combination

        #this shit is easy for 1 coupon     (just check if each coupon is applicable)
        #this shit is easy for 2 coupons    (just create a 2x2 table/matrix, and check is each value is applicable)
        # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^    this can be optimized by checking for c1 then generating new tot price,
        # then test is c2 is applicable against new price
        # this efficent method could scale well to more coupons, need to check this
        
        # the easy to implement way is to create a X dimentional data structure, where X is the number of coupons.
        # then generate the price for each combination, but this gets computationally expensive - fast.
        # the better way would be the ABOVE cumsum tree.
        # 
        # so implement CUMSUM tree for all coupons
        # a potential complication is that each node can be used once OR MORE
        pass

    # generate all possible item combinations, <coupon_count_combo_range> groups
    all_item_groups = list[list[CartItem]]  # use this simple data structure and calculate the tot price on the fly
    for item_group_count in coupon_count_combo_range:
        # for one group this is just all the cart items
        # for 2 items this is (<number cart items> choose 2) options
        # for 3 items this is (<number cart items> choose 3) options
        # demo:
        # cart: [1,2,3]
        # 1:    ([1,2,3])
        # 2:    ([1], [2,3]), ([2],[1,3]), ([3],[1,2])
        # 3:    ([1]), ([2]), ([3]) - redundant?
        # note for 3 groups example: matching a coupon combo to an item will be a nigtmare...
        # maybe dont consider this option, as this is not reallistic
        

        pass
    
    # after generating all the combinations of coupons and cart items:
    # find some way to "pit them" against each other:
    # this is done by group count:
    # i.e. X COUPONS VS A COMBINATION OF ITEMS SORTED INTO X GROUPS  

    # ok this is complex as fuckkkkkkkkkk
    # implement this in in the easy way, one coupop, then 2 coupons

    #maybe this algoritm could be optimised with the assumption:
    # of both coupons and cart items are sorted by price????????  

    # max_coupons_needed = math.ceil(total_amount / min(coupon.min_total_amount for coupon in available_coupons))
    


if __name__ == "__main__":
    main()