from five import grok

from kk.shopified.utils import get_cart
from kk.shopified.utils import wipe_cart

from Products.CMFCore.interfaces import IContentish


class ConfirmationView(grok.View):
    grok.context(IContentish)
    grok.require('zope2.View')
    grok.name('order-confirmation')

    def update(self):
        cart = get_cart()
        order_id = self.request.get('oid', '')
        self.txn_id = cart['txn_id']
        import pdb; pdb.set_trace( )
        if self.is_equal(order_id, self.txn_id):
            wipe_cart()

    def is_equal(self, a, b):
        if len(a) != len(b):
            return False
        result = 0
        for x, y in zip(a, b):
            result |= ord(x) ^ ord(y)
        return result == 0
