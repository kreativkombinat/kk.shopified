from five import grok
from zope.interface import implements
from zope.globalrequest import getRequest
from zope.annotation.interfaces import IAttributeAnnotatable

from collective.beaker.interfaces import ISession

from kk.shopified.interfaces import IShoppingCartUtility
from kk.shopified.interfaces import IShoppingCart


class ShoppingCartUtility(grok.GlobalUtility):
    implements(IShoppingCartUtility)

    def get(self, portal, key=None):
        cart_id = 'kk.shopified.cart.%s' % '/'.join(
            portal.getPhysicalPath())
        session = ISession(getRequest())
        if cart_id not in session:
            session[cart_id] = ShoppingCart()
            session.save()
        return session[cart_id]

    def destroy(self, portal, key=None):
        cart_id = 'kk.shopified.cart.%s' % '/'.join(
            portal.getPhysicalPath())
        session = ISession(getRequest())
        if cart_id in session:
            del session[cart_id]
            session.save()


class ShoppingCart(object):
    implements(IShoppingCart, IAttributeAnnotatable)

    def data(self):
        data = dict()
        return data
