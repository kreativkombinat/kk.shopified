from zope.interface import Interface
from kk.shopified.utils import format_price


class IShopified(Interface):
    """ Generic interface usable as a marker """


class IShoppingCart(Interface):
    """ Implemented by the shoppping cart object and providing a dictionary
    """

    def netprice(self, items):
        """Calculate net sum of cart items.
        """
        raise NotImplementedError(u"CartDataProviderBase does not implement "
                                  u"``net``.")

    def vat(self, items):
        """Calculate vat sum of cart items.
        """
        raise NotImplementedError(u"CartDataProviderBase does not implement "
                                  u"``vat``.")

    def cart_items(self):
        """ Return a list of cart items. The lsit will be extracted from the
            current session
        """

    def item(self, uid, title, count, price, url):
        """
        @param uid: catalog uid
        @param title: string
        @param count: item count as int
        @param price: item price as float
        @param url: item URL
        """
        return {
            'cart_item_uid': uid,
            'cart_item_title': title,
            'cart_item_count': count,
            'cart_item_price': format_price(price),
            'cart_item_location:href': url,
        }

    @property
    def data(self):
        ret = {
            'cart_items': list(),
            'cart_summary': dict(),
        }
        items = self.cart_items()
        if items:
            net = self.netprice(items)
            vat = self.vat(items)
            cart_items = self.cart_items(items)
            ret['cart_items'] = cart_items
            ret['cart_summary']['cart_net'] = format_price(net)
            ret['cart_summary']['cart_vat'] = format_price(vat)
            ret['cart_summary']['cart_total'] = format_price(net + vat)
            ret['cart_summary']['cart_total_raw'] = net + vat
        return ret
