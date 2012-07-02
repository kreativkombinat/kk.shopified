from zope.interface import Interface
#from kk.shopified.utils import format_price


class IShopified(Interface):
    """ Generic interface usable as a marker """


class IShoppingCartUtility(Interface):

    def get(context):
        """
        Return the user's shopping cart or none if not found. If
        no cart is available create a new one.
        """

    def destroy(context):
        """ Remove the current user's cart from the session if it exists. """


class IShoppingCart(Interface):
    """ Implemented by the shoppping cart object and providing a dictionary
    """
