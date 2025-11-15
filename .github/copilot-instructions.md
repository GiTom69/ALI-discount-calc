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
- `load_cart_items_from_file(cart_file_path)`: Parse cart data from text file
- `load_coupons_from_file(coupons_file_path)`: Parse coupon data from text file
- Default file paths: `cart.txt` and `coupons.txt`

### Optimization Logic
- Generate all possible coupon combinations
- Filter applicable combinations based on cart total
- Calculate maximum savings for each valid combination
- Find optimal coupon stack that maximizes discount

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
- ⚠️ File parsing functions need implementation
- ⚠️ Coupon combination generation logic in progress
- ⚠️ Optimization algorithm needs refinement

## When Generating Code
- Maintain existing validation patterns
- Use list comprehensions for filtering and transformations
- Add helpful comments for complex logic
- Follow the established docstring format
- Consider edge cases in discount calculations
