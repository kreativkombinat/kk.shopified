from five import grok

from kk.shopified.utils import get_cart
from kk.shopified.interfaces import ICartUpdaterUtility


class CartUpdaterUtility(grok.GlobalUtility):
    grok.provides(ICartUpdaterUtility)

    def add(self, item_uuid, quantity=1):
        """
            Add item to shopping cart
        """
        cart = get_cart()
        qty = int(quantity)
        item = self.is_incremental_update(item_uuid, qty)
        if not item:
            cart[item_uuid] = qty
            return cart[item_uuid]

    def delete(self, item_uuid):
        """ Remove item from shopping cart """
        cart = get_cart()
        if item_uuid in cart:
            del cart[item_uuid]
            return item_uuid

    def is_incremental_update(self, product_code, quantity):
        cart = get_cart()
        item_id = product_code
        if item_id in cart:
            cart[item_id] = quantity
            return cart[item_id]
        return None
