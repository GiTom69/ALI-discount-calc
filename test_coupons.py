"""Test script for load_coupons_from_file function"""
import pathlib
from main import load_coupons_from_file

def test_coupon_file(file_path: str):
    """Test loading coupons from a file and display results"""
    print(f"\n{'='*60}")
    print(f"Testing: {file_path}")
    print(f"{'='*60}")
    
    try:
        coupons = load_coupons_from_file(file_path)
        print(f"✓ Successfully loaded {len(coupons)} coupons\n")
        
        # Group by discount/min_amount to show duplicates
        from collections import defaultdict
        grouped = defaultdict(list)
        
        for coupon in coupons:
            key = (coupon.discount, coupon.min_total_amount)
            grouped[key].append(coupon.code)
        
        # Display grouped results
        for (discount, min_amount), codes in sorted(grouped.items(), key=lambda x: x[0][1]):
            percentage = (discount / min_amount) * 100
            print(f"💰 ${discount:.0f} off on ${min_amount:.0f}+ ({percentage:.1f}%)")
            print(f"   Codes: {', '.join(codes)}")
            print()
        
        return coupons
        
    except FileNotFoundError as e:
        print(f"✗ Error: {e}")
        return []
    except ValueError as e:
        print(f"✗ Error: {e}")
        return []
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    # Test both example files
    example_dir = pathlib.Path("example data")
    
    if example_dir.exists():
        coupon_files = list(example_dir.glob("coupons*.txt"))
        
        if coupon_files:
            all_coupons = []
            for coupon_file in sorted(coupon_files):
                coupons = test_coupon_file(str(coupon_file))
                all_coupons.extend(coupons)
            
            print(f"\n{'='*60}")
            print(f"SUMMARY: Total {len(all_coupons)} coupons loaded from {len(coupon_files)} files")
            print(f"{'='*60}")
        else:
            print("No coupon files found in 'example data' directory")
    else:
        print("'example data' directory not found")
        print("\nTrying current directory...")
        
        # Try files in current directory
        for filename in ["coupons.txt", "coupons 1.txt", "coupons 2.txt"]:
            if pathlib.Path(filename).exists():
                test_coupon_file(filename)
