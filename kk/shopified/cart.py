from five import grok
from zope.interface import Interface
from zope.interface import implements
from zope.globalrequest import getRequest
from getpaid.core.cart import ShoppingCart
from collective.beaker.interfaces import ISession


class IShoppingCartUtility(Interface):

    def get(context):
        """
        Return the user's shopping cart or none if not found. If
        no cart is available create a new one.
        """

    def destroy(context):
        """ Remove the current user's cart from the session if it exists. """


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
