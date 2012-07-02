from five import grok
from Acquisition import aq_inner

from Products.CMFCore.interfaces import IContentish

from kk.shopified.utils import get_cart


class ShoppingCartView(grok.View):
    grok.context(IContentish)
    grok.require('zope2.View')
    grok.name('cart-overview')

    def update(self):
        context = aq_inner(self.context)
        self.context_url = context.absolute_url()

    def cart(self):
        cart = get_cart()
        return cart
