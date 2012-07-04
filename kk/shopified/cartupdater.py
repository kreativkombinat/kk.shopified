from five import grok
from zope.annotation.interfaces import IAnnotations

from kk.shopified.utils import get_cart
from kk.shopified.interfaces import ICartUpdaterUtility


class CartUpdaterUtility(grok.GlobalUtility):
    grok.provides(ICartUpdaterUtility)

    def add(self, item_uuid, quantity=1):
        """
            Add item to shopping cart
        """
        key = 'kk.shopified.cartitem'
        cart = get_cart()
        annotations = IAnnotations(cart, None)
        qty = int(quantity)
        cartitem = {}
        cartitem['product_uuid'] = item_uuid
        cartitem['quantity'] = qty
        if annotations is not None:
            cartitems = annotations.get(key, dict())
            cartitems = cartitems.append(cartitem)
            annotations[key] = cartitems
        item = self.is_incremental_update(item_uuid, qty)
        if not item:
            cart[item_uuid] = qty
            return cart[item_uuid]

    def is_incremental_update(self, product_code, quantity):
        cart = get_cart()
        item_id = product_code
        if item_id in cart:
            cart[item_id] = quantity
            return cart[item_id]
        return None
