from zope.interface import Interface
from zope.interface import Attribute
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

    data = Attribute(u"Cart data as list of dicts.")


class ICartUpdaterUtility(Interface):
    """ Utility to update the cart. This utility is callable format_price
        external product implementations as a plugin point
    """

    def add(context):
        """ Add an item to the shopping cart

            @param product_uuid: catalog uuid
            @param quantity: item quantity
        """

    def delete(context):
        """ Delete an item from the shopping cart

            @param product_uuid: catalog uuid
        """

    def update(context):
        """ update an item in the shopping cart

            @param product_uuid: catalog uuid
            @param quantity: item quantity
        """
