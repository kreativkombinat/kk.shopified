from five import grok
from zope.interface import Interface
from plone.app.layout.viewlets.interfaces import IPortalHeader
from kk.shopified.utils import get_cart


class CartViewlet(grok.Viewlet):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.viewletmanager(IPortalHeader)
    grok.name('kk.shopified.CartViewlet')

    def update(self):
        self.available = len(self.cart()) > 0

    def cart(self):
        cart = get_cart()
        return cart

    def count_items(self):
        return len(self.cart())
