# Copilot Instructions for ALI Discount Calculator

## Project Overview
This is a Python application for calculating optimal coupon combinations for AliExpress shopping cart discounts. The goal is to find the best combination of coupons to maximize savings on a cart of items.

## Code Style & Conventions
- **Language**: Python 3.x
- **Type Hints**: Use type hints for all function parameters and return values
- **Docstrings**: Use Google-style docstrings for all classes and methods
- **Naming**: Use `snake_case` for functions and variables, `PascalCase` for classes
- **Validation**: Include comprehensive input validation with clear error messages

## Key Classes

### `Coupon`
Represents a coupon with:
- `code`: Coupon identifier (str)
- `min_total_amount`: Minimum order amount to apply coupon (float)
- `discount`: Discount amount in currency units (float)

Important methods:
- `is_applicable(total_amount)`: Check if coupon can be used
- `apply_discount(total_amount)`: Calculate discounted amount
- `get_percentage_discount()`: Return discount as a ratio (0.0-1.0)

### `CartItem`
Represents a shopping cart item with:
- `name`, `variant`: Item identification
- `price`: Current price (USD)
- `quantity`: Number of items
- `original_price`, `savings`, `shipping`: Pricing details
- `store`, `stock_note`: Additional metadata

## Core Functionality

### File Processing
- `load_cart_items_from_file(cart_file_path)`: Parse AliExpress cart data from text file
  - Handles multi-line product names
  - Extracts variant, prices, shipping, store info
  - Skips URLs and navigation elements
  - Returns list of `CartItem` objects
- `load_coupons_from_file(coupons_file_path, max_rows_for_coupon=5)`: Parse coupon data
  - Auto-detects emoji-based formatting
  - Supports multiple currencies: $, USD, ₪, NIS, ILS, €, EUR, £, GBP
  - Extracts min amounts, discounts, and coupon codes
  - Creates separate `Coupon` instance for each code
- Default file paths: `cart.txt` and `coupons.txt`

### Optimization Logic (In Progress)
Current approach:
1. Generate all valid coupon combinations (filtered by total cart value)
2. Generate all item groupings (by number of groups matching coupon count)
3. Match item groups to coupon groups where item_total >= coupon_min_total
4. **TODO**: Calculate final discounted prices for each valid pairing
5. **TODO**: Find optimal combination that maximizes total discount

Key functions:
- `generate_all_coupon_combinations()`: Creates all valid coupon combos up to max_coupons
- `generate_n_coupon_combinations()`: Creates n-sized coupon groups under discount limit
- `generate_item_combinations()`: Creates all possible item combinations
- `generate_n_item_combinations()`: Creates n-sized item groups
- `calc_tot_coupons_cost()`: Sums discount amounts
- `calc_tot_items_cost()`: Sums item costs
- `get_max_coupons_needed()`: Determines worst-case coupon count needed

## Implementation Guidelines

1. **Error Handling**: Always validate inputs and raise descriptive `ValueError` exceptions
2. **Float Precision**: Be mindful of floating-point arithmetic for currency calculations
3. **Performance**: Consider computational complexity when generating coupon combinations
4. **Edge Cases**: Handle scenarios like:
   - Empty carts or coupon lists
   - Coupons with discounts exceeding order total
   - Multiple coupons with overlapping thresholds

## Current Development Status
- ✅ Base classes (`Coupon`, `CartItem`) implemented with validation
- ✅ File parsing functions implemented:
  - `load_cart_items_from_file()`: Parses AliExpress cart text files
  - `load_coupons_from_file()`: Parses coupon data with emoji detection and multi-currency support
- ✅ Coupon combination generation logic implemented:
  - `generate_all_coupon_combinations()`: Generates all valid coupon combinations
  - `generate_n_coupon_combinations()`: Generates n-sized coupon groups
  - `calc_tot_coupons_cost()`: Calculates total discount from coupon list
- ✅ Item combination generation logic implemented:
  - `generate_item_combinations()`: Generates all item combinations
  - `generate_n_item_combinations()`: Generates n-sized item groups
  - `calc_tot_items_cost()`: Calculates total cost of items
- ✅ Helper utilities:
  - `get_max_coupons_needed()`: Calculates maximum coupons needed for a total
- ⚠️ Main optimization algorithm in progress:
  - Item-to-coupon matching logic needs completion
  - Need to implement optimal pairing algorithm between item groups and coupon groups
  - Final best-combination selection logic needed

## When Generating Code
- Maintain existing validation patterns
- Use list comprehensions for filtering and transformations
- Add helpful comments for complex logic
- Follow the established docstring format
- Consider edge cases in discount calculations
