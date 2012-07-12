from five import grok
from zope.interface import implements
from zope.globalrequest import getRequest

from collective.beaker.interfaces import ISession
from kk.shopified.interfaces import IShoppingCartUtility


class ShoppingCartUtility(grok.GlobalUtility):
    implements(IShoppingCartUtility)

    def get(self, portal, key=None):
        cart_id = 'kk.shopified.cart.%s' % '/'.join(
            portal.getPhysicalPath())
        session = ISession(getRequest())
        if cart_id not in session:
            session[cart_id] = dict()
            session.save()
        return session[cart_id]

    def destroy(self, portal, key=None):
        cart_id = 'kk.shopified.cart.%s' % '/'.join(
            portal.getPhysicalPath())
        session = ISession(getRequest())
        if cart_id in session:
            del session[cart_id]
            session.save()
