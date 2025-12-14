import pathlib
import re
from itertools import combinations, chain

class Coupon:
    min_total_amount = 0.0  # Minimum amount to apply the coupon
    discount = 0.0          # Discount amount
    code = ""               # Single coupon code
    def __init__(self, code: str, min_total_amount: float, discount: float):
        """
        Initialize a Coupon instance.
        Args:
            code (str): The coupon code (single code only).
            min_total_amount (float): The minimum total amount required to apply the coupon.
            discount (float): The discount percentage to be applied.
        """
        if not isinstance(code, str):
            raise ValueError("Code must be a string.")
        
        self.code = code.strip()
        
        if not self.code:
            raise ValueError("Coupon code cannot be empty.")
        
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
        return f"Coupon(code={self.code}, min_total_amount={self.min_total_amount}, discount={self.discount}%)"

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

COUPONS_FILE_PATH = "example data\coupons 1.txt"
CART_FILE_PATH = "example data\Shopping Cart1.txt"

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
                
                # ignore this error for now, set quantity to 1
                # item_data['quantity'] = 1
                # item_data['stock_note'] = ''
                
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

def load_coupons_from_file(coupons_file_path: str,
                           max_rows_for_coupon: int = 5) -> list[Coupon]:
    """
    Load coupons from a text file.
    
    Logic:
    - Detect if file contains emojis
    - If emojis exist: Each coupon starts at an emoji line and continues until:
      * Same currency detected twice (min_amount and discount)
      * One or more codes found
      * max_rows_for_coupon reached
    - If no emojis: Parse lines detecting currency amounts and codes
    
    Supports currencies: $, USD, ₪, NIS, ILS, €, EUR, £, GBP
    
    Args:
        coupons_file_path (str): Path to the coupons file.
        
    Returns:
        list[Coupon]: List of Coupon objects parsed from the file.
        Each code becomes a separate Coupon instance.
        
    Raises:
        FileNotFoundError: If the coupons file doesn't exist.
        ValueError: If the file format is invalid or cannot be parsed.
    """
    
    coupons_path = pathlib.Path(coupons_file_path)
    if not coupons_path.exists():
        raise FileNotFoundError(f"Coupons file not found: {coupons_file_path}")
    
    content = None

    with open(coupons_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # Check if file contains emojis
    emoji_pattern = r'[\U0001F300-\U0001F9FF]|[\U00002600-\U000027BF]'
    has_emojis = any(re.search(emoji_pattern, line) for line in lines)
    
    # Currency patterns (matches: $10, 10$, US $10, 10 USD, ₪10, 10 NIS, etc.)
    currency_pattern = r'(?:US\s*)?(?:[$₪€£])\s*(\d+(?:\.\d+)?)|(\d+(?:\.\d+)?)\s*(?:[$₪€£]|USD|NIS|ILS|EUR|GBP)'
    
    # Coupon code pattern (alphanumeric codes, typically 6-10 characters)
    code_pattern = r'\b([A-Z0-9]{6,12})\b'
    
    coupons = []
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines and common headers/footers
        if (not line or 
            line.startswith('http') or
            line.startswith('www.') or
            'click' in line.lower() and 'here' in line.lower()):
            i += 1
            continue
        
        # Check if this line could start a coupon entry
        has_emoji_here = bool(re.search(emoji_pattern, line)) if has_emojis else True
        has_currency_here = bool(re.search(currency_pattern, line))
        
        # Skip if emojis expected but not found, or no currency info
        if has_emojis and not has_emoji_here:
            i += 1
            continue
        
        if not has_currency_here:
            i += 1
            continue
        
        # Start collecting data for a coupon (possibly multi-line)
        collected_lines = []
        rows_collected = 0
        
        while i < len(lines) and rows_collected < max_rows_for_coupon:
            current_line = lines[i].strip()
            
            # Stop at next emoji (start of new coupon) if we already collected something
            if rows_collected > 0 and has_emojis and re.search(emoji_pattern, current_line):
                break
            
            # Stop at URLs or major section breaks
            if current_line.startswith('http') or current_line.startswith('www.'):
                break
            
            if current_line:
                collected_lines.append(current_line)
                rows_collected += 1
            
            i += 1
        
        # Parse collected lines to extract amounts and codes
        combined_text = ' '.join(collected_lines)
        
        # Extract all currency amounts
        amounts = []
        for match in re.finditer(currency_pattern, combined_text):
            amount_str = match.group(1) if match.group(1) else match.group(2)
            if amount_str:
                amounts.append(float(amount_str))
        
        # Extract all coupon codes
        codes = []
        for match in re.finditer(code_pattern, combined_text):
            code = match.group(1)
            # Filter out common non-code words that might match the pattern
            if code not in ['HTTPS', 'HTTP', 'CLICK', 'COUPON']:
                codes.append(code)
        
        # Validate: need at least 2 amounts (discount and min_amount) and at least 1 code
        if len(amounts) >= 2 and len(codes) >= 1:
            # Typically: first amount is discount, second is min_amount
            # Or could be reversed depending on format
            # Use heuristic: smaller value is usually discount, larger is min_amount
            if amounts[0] < amounts[1]:
                discount = amounts[0]
                min_amount = amounts[1]
            else:
                discount = amounts[1]
                min_amount = amounts[0]
            
            # Create separate Coupon for each code
            for code in codes:
                try:
                    coupon = Coupon(code, min_amount, discount)
                    coupons.append(coupon)
                except ValueError:
                    # Skip invalid coupons
                    pass
    
    if not coupons:
        raise ValueError("No valid coupons found in file. Please check the file format.")
    
    return coupons

def tot_coupons_cost(coupons: list[Coupon]) -> float:
    """
    Calculate the total discount amount from a list of coupons.
    Args:
        coupons (list[Coupon]): List of Coupon objects.

    Returns:
        float: Total discount amount.
    """
    return sum(coupon.discount for coupon in coupons)

def tot_items_cost(items: list[CartItem] | tuple[CartItem]) -> float:
    """
    Calculate the total cost of a list of cart items.
    Args:
        items (list[CartItem] | tuple[CartItem]): Collection of CartItem objects.
    Returns:
        float: Total cost of all items.
    """
    return sum(item.get_total_price() for item in items)

def generate_n_coupon_combinations(coupon_list:list[Coupon],
                                   n: int,
                                   max_tot_discount: float | None = None) -> list[list[Coupon]]:
    """
    Generate possible combinations n of coupons, where the sum of coupon discounts is less than max_tot_discount.
    Args:
        coupon_list         (list[Coupon]): List of Coupon objects to generate sub-groups from.
        n                   (int):          number of Coupon objects in each sub-groups.
        max_tot_discount    (float | None): the maximum sum of all coupon discounts in a sub-groups.
    Returns:
        list[list[Coupon]]: List of lists, each containing a combination of Coupon objects.
    """
    n_coupon_combs = combinations(coupon_list, n)

    if max_tot_discount is None:
        return list(n_coupon_combs)
    
    return [comb for comb in n_coupon_combs if tot_coupons_cost(comb) <= max_tot_discount]

    # return list(chain.from_iterable(combinations(coupons, r) for r in range(1, max_coupons + 1)))

def generate_n_item_combinations(item_list: list[CartItem],
                                 n: int) -> list[tuple[CartItem]]:
    """
    Generate possible combinations of n cart items.
    Args:
        item_list (list[CartItem]): List of CartItem objects to generate sub-groups from.
        n (int): Number of CartItem objects in each sub-group.
    Returns:
        list[tuple[CartItem]]: List of tuples, each containing a combination of CartItem objects.
    """
    if not item_list or n < 1 or n > len(item_list):
        return []
    
    return list(combinations(item_list, n))

def get_max_coupons_needed(total_amount: float, coupons: list[Coupon]) -> int:
    """
    Calculate the maximum number of coupons needed to reach the total amount.
    Args:
        total_amount (float): The total amount to reach.
        coupons (list[Coupon]): List of Coupon objects.
    Returns:
        int: Maximum number of coupons needed.
    """
    if total_amount <= 0 or not coupons:
        return 0

    # Sort coupons by their price (ascending)
    sorted_coupons = sorted(coupons, key=lambda c: c.min_total_amount)

    max_coupons = 0
    current_total = 0.0

    for coupon in sorted_coupons:
        current_total += coupon.discount
        max_coupons += 1
        if current_total >= total_amount:
            break

    return max_coupons

def get_items_left(items: list[CartItem], used_items: list[CartItem]) -> list[CartItem]:
    """
    Get the list of cart items that are not in the used_items list.
    Args:
        items (list[CartItem]): List of all CartItem objects.
        used_items (list[CartItem]): List of CartItem objects that have been used.
    Returns:
        list[CartItem]: List of CartItem objects that are not in used_items.
    """
    used_set = set(used_items)
    return [item for item in items if item not in used_set]

def get_best_single_coupon(coupons: list[Coupon], item_total: float) -> Coupon | None:
    """
    Get the best single coupon that can be applied to the given item total.
    Args:
        coupons (list[Coupon]): List of Coupon objects.
        item_total (float): The total amount of the items.
    Returns:
        Coupon | None: The best applicable Coupon object, or None if no coupon is applicable.
    """
    applicable_coupons = [coupon for coupon in coupons if coupon.is_applicable(item_total)]
    if not applicable_coupons:
        return None
    
    # Return the coupon with the highest discount
    return max(applicable_coupons, key=lambda c: c.discount)

def generate_cart_splits(cart_items: list[CartItem], n_splits: int) -> list[list[list[CartItem]]]:
    """
    Generate all possible ways to split cart items into n_splits groups.
    Args:
        cart_items (list[CartItem]): List of CartItem objects.
        n_splits (int): Number of groups to split the cart items into.
    Returns:
        list[list[list[CartItem]]]: List of ways to split the cart items into n_splits groups.
    """
    # This is a complex combinatorial problem; a full implementation is non-trivial.
    # Placeholder for actual implementation.
    pass

# ============================================================================
# Step A: Preparation & Pre-filtering
# ============================================================================

def clean_coupons(coupons: list[Coupon], total_cart_value: float) -> list[Coupon]:
    """
    Remove coupons where min_total_amount > total_cart_value.
    
    Args:
        coupons (list[Coupon]): List of all available coupons.
        total_cart_value (float): Total value of all cart items.
    
    Returns:
        list[Coupon]: Filtered list of applicable coupons.
    """
    return [coupon for coupon in coupons if coupon.min_total_amount <= total_cart_value]

def sort_items_by_price_desc(items: list[CartItem]) -> list[CartItem]:
    """
    Sort cart items by price in descending order.
    This helps the backtracking algorithm fail faster on invalid branches.
    
    Args:
        items (list[CartItem]): List of CartItem objects.
    
    Returns:
        list[CartItem]: Sorted list of CartItem objects (descending by price).
    """
    return sorted(items, key=lambda item: item.get_total_price(), reverse=True)

# ============================================================================
# Step B: Generate Coupon Combinations
# ============================================================================

def generate_all_coupon_subsets(coupons: list[Coupon], total_cart_value: float) -> list[tuple[list[Coupon], float]]:
    """
    Generate all possible subsets of coupons, calculate total discount for each,
    sort by total discount descending, and filter infeasible subsets.
    
    Args:
        coupons (list[Coupon]): List of available coupons.
        total_cart_value (float): Total value of all cart items.
    
    Returns:
        list[tuple[list[Coupon], float]]: List of (coupon_subset, total_discount) tuples,
                                           sorted by total_discount descending.
    """
    all_subsets = []
    
    # Generate all non-empty subsets (from size 1 to len(coupons))
    for r in range(1, len(coupons) + 1):
        for subset in combinations(coupons, r):
            subset_list = list(subset)
            total_discount = tot_coupons_cost(subset_list)
            
            # Filter: sum of min_total_amount must not exceed total_cart_value
            sum_min_amounts = sum(coupon.min_total_amount for coupon in subset_list)
            
            if sum_min_amounts <= total_cart_value:
                all_subsets.append((subset_list, total_discount))
    
    # Sort by total_discount descending (best discounts first)
    all_subsets.sort(key=lambda x: x[1], reverse=True)
    
    return all_subsets

# ============================================================================
# Step C: Feasibility Check (Recursive Backtracking)
# ============================================================================

def can_partition_items(items: list[CartItem], 
                        coupons: list[Coupon]) -> tuple[bool, list[list[CartItem]] | None]:
    """
    Check if cart items can be partitioned into groups such that each group
    satisfies the min_total_amount requirement of its corresponding coupon.
    
    Uses recursive backtracking with forward checking optimization.
    
    Args:
        items (list[CartItem]): List of cart items (should be sorted by price desc).
        coupons (list[Coupon]): List of coupons (one per group).
    
    Returns:
        tuple[bool, list[list[CartItem]] | None]: 
            - True and the partition if feasible
            - False and None if not feasible
    """
    n_groups = len(coupons)
    n_items = len(items)
    
    # Initialize groups
    groups: list[list[CartItem]] = [[] for _ in range(n_groups)]
    group_totals: list[float] = [0.0] * n_groups
    
    # Calculate total remaining value for all items
    item_prices = [item.get_total_price() for item in items]
    
    def backtrack(item_index: int) -> bool:
        """
        Recursive backtracking function.
        
        Args:
            item_index (int): Current item index being placed.
        
        Returns:
            bool: True if a valid partition is found, False otherwise.
        """
        # Base case: all items have been placed
        if item_index == n_items:
            # Check if all groups meet their minimum requirements
            for i in range(n_groups):
                if group_totals[i] < coupons[i].min_total_amount:
                    return False
            return True
        
        # Calculate remaining cart value (items not yet placed)
        remaining_value = sum(item_prices[item_index:])
        
        current_item = items[item_index]
        current_item_price = item_prices[item_index]
        
        # Try placing current item in each group
        for group_idx in range(n_groups):
            # Add item to group
            groups[group_idx].append(current_item)
            group_totals[group_idx] += current_item_price
            
            # Forward Checking (Pruning):
            # Check if remaining items can possibly satisfy unmet requirements
            can_continue = True
            for i in range(n_groups):
                remaining_needed = coupons[i].min_total_amount - group_totals[i]
                # If this group needs more than what's remaining (including current item's contribution)
                if remaining_needed > remaining_value:
                    can_continue = False
                    break
            
            # Recurse if forward checking passes
            if can_continue and backtrack(item_index + 1):
                return True
            
            # Backtrack: remove item from group
            groups[group_idx].pop()
            group_totals[group_idx] -= current_item_price
        
        return False
    
    # Start backtracking
    success = backtrack(0)
    
    if success:
        # Return deep copy of groups to preserve the solution
        return True, [group[:] for group in groups]
    else:
        return False, None

def find_optimal_coupon_combination(items: list[CartItem], 
                                    coupons: list[Coupon]) -> tuple[list[Coupon], list[list[CartItem]], float] | None:
    """
    Find the optimal coupon combination that maximizes total discount.
    
    Implements the complete algorithm:
    - Step A: Clean and prepare inputs
    - Step B: Generate and sort coupon subsets
    - Step C: Check feasibility with backtracking
    
    Args:
        items (list[CartItem]): List of cart items.
        coupons (list[Coupon]): List of available coupons.
    
    Returns:
        tuple[list[Coupon], list[list[CartItem]], float] | None:
            - (selected_coupons, item_groups, total_discount) if solution found
            - None if no valid combination exists
    """
    # Step A: Preparation & Pre-filtering
    total_cart_value = tot_items_cost(items)
    
    # Clean coupons (remove those with min_total_amount > total_cart_value)
    valid_coupons = clean_coupons(coupons, total_cart_value)
    
    if not valid_coupons:
        return None
    
    # Sort items by price descending
    sorted_items = sort_items_by_price_desc(items)
    
    # Step B: Generate Coupon Combinations
    coupon_subsets = generate_all_coupon_subsets(valid_coupons, total_cart_value)
    
    if not coupon_subsets:
        return None
    
    # Step C: Feasibility Check
    # Iterate through coupon subsets (already sorted by total_discount descending)
    for coupon_subset, total_discount in coupon_subsets:
        # Try to partition items for this coupon subset
        feasible, item_partition = can_partition_items(sorted_items, coupon_subset)
        
        if feasible:
            # Found the optimal solution (first feasible one with highest discount)
            return coupon_subset, item_partition, total_discount
    
    # No feasible solution found
    return None


def main():
    # Load cart items
    my_cart = load_cart_items_from_file(CART_FILE_PATH)
    if not my_cart:
        print("Cart is empty.")
        return
    
    print("=" * 80)
    print("Cart items loaded:")
    print("=" * 80)
    total_cart_value = tot_items_cost(my_cart)
    for item in my_cart:
        print(f" - {item.name[:50]:50s} ${item.get_total_price():7.2f}")
    print("-" * 80)
    print(f"{'Total Cart Value:':50s} ${total_cart_value:7.2f}")
    print("=" * 80)
    print()
    
    # Load coupons
    available_coupons = load_coupons_from_file(COUPONS_FILE_PATH)
    if not available_coupons:
        print("No available coupons.")
        return
    
    print("Available coupons:")
    print("=" * 80)
    for coupon in available_coupons:
        print(f" - {coupon.code:12s} Min: ${coupon.min_total_amount:7.2f} Discount: ${coupon.discount:7.2f}")
    print("=" * 80)
    print()
    
    # Find optimal coupon combination
    print("Finding optimal coupon combination...")
    result = find_optimal_coupon_combination(my_cart, available_coupons)
    
    if result is None:
        print("\nNo valid coupon combination found.")
        print("This could mean:")
        print(" - No single coupon or combination meets the minimum requirements")
        print(" - Cart items cannot be split to satisfy multiple coupons")
        return
    
    selected_coupons, item_groups, total_discount = result
    
    # Display results
    print("\n" + "=" * 80)
    print("OPTIMAL SOLUTION FOUND!")
    print("=" * 80)
    print(f"\nTotal Discount: ${total_discount:.2f}")
    print(f"Final Price: ${total_cart_value - total_discount:.2f}")
    print(f"Savings: {(total_discount / total_cart_value * 100):.1f}%")
    print("\n" + "-" * 80)
    print("Coupon Usage:")
    print("-" * 80)
    
    for i, (coupon, item_group) in enumerate(zip(selected_coupons, item_groups), 1):
        group_total = tot_items_cost(item_group)
        group_discount = coupon.discount
        group_final = group_total - group_discount
        
        print(f"\nGroup {i}: Coupon {coupon.code}")
        print(f"  Min Required: ${coupon.min_total_amount:.2f}")
        print(f"  Group Total:  ${group_total:.2f}")
        print(f"  Discount:     ${group_discount:.2f}")
        print(f"  Final:        ${group_final:.2f}")
        print(f"  Items in group:")
        for item in item_group:
            print(f"    - {item.name[:45]:45s} ${item.get_total_price():7.2f}")
    
    print("\n" + "=" * 80)
    

if __name__ == "__main__":
    main()