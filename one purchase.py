from main import Coupon, CartItem
from main import load_cart_items_from_file, load_coupons_from_file

COUPONS_FILE_PATH = "coupons.txt"
CART_FILE_PATH =    "cart.txt"

def get_items_total(items_list:list) -> float:
    tot_items_cost = 0.0
    for item in items_list:
        tot_items_cost += item.get_total_price()

    return  tot_items_cost

def find_best_dicount_coupon(coupons_list: list[Coupon], tot_cost:float) -> Coupon | None:
    best_coupon = Coupon("NA",0,0) #inisitallized as always applicable but no discount
    for c in coupons_list:
        if c.is_applicable(tot_cost):
            if c.discount > best_coupon.discount:
                best_coupon = c

    if best_coupon.codes == "NA":
        return None

    return best_coupon


def main():
    my_coupons  :list[Coupon] =     load_coupons_from_file(COUPONS_FILE_PATH)
    my_items    :list[CartItem] =   load_cart_items_from_file(CART_FILE_PATH)

    items_tot =     get_items_total(my_items)
    best_coupon =   find_best_dicount_coupon(my_coupons, items_tot)

    if best_coupon:
        print("the best coupon is ", best_coupon)
    
    else:
        print("no matching coupons found")



if __name__ == "__main__":

    main()