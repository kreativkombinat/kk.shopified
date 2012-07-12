from five import grok
from zope.interface import Interface
from zope.component import getUtility
from zope.component import getMultiAdapter
from plone.app.layout.viewlets.interfaces import IPortalHeader
from plone.registry.interfaces import IRegistry

from kk.shopified.utils import get_cart
from kk.shopified.interfaces import IShopifiedSettings


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

    def cart_url(self):
        pstate = getMultiAdapter((self.context, self.request),
                                name=u"plone_portal_state")
        portal_url = pstate.portal_url()
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IShopifiedSettings)
        shop_url = settings.shop_url
        url = portal_url + shop_url + '/@@cart'
        return url
