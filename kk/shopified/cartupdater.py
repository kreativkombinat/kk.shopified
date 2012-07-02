from five import grok
from zope.annotation.interfaces import IAnnotations

from plone.app.uuid.utils import uuidToObject

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
        product = self.product_from_uuid(item_uuid)
        qty = int(quantity)
        cartitem = {}
        cartitem['product_uuid'] = item_uuid
        cartitem['quantity'] = qty
        if annotations is not None:
            cartitems = annotations.get(key, dict())
            cartitems = cartitems.append(cartitem)
            annotations[key] = cartitems
        product_id = product.product_code
        item = self.is_incremental_update(product_id, qty)
        if not item:
            cart[product_id] = cartitem
            return cartitem

    def is_incremental_update(self, product_code, quantity):
        cart = get_cart()
        item_id = product_code
        if item_id in cart:
            cart[item_id].quantity = quantity
            return cart[item_id]
        return None

    def product_from_uuid(self, uid):
        product = uuidToObject(uid)
        return product
