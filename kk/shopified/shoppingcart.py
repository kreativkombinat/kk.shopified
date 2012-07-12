from five import grok
from Acquisition import aq_inner
from AccessControl import Unauthorized
from zope.component import getMultiAdapter

from plone.app.uuid.utils import uuidToObject

from Products.statusmessages.interfaces import IStatusMessage
from plone.uuid.interfaces import IUUID
from Products.CMFCore.interfaces import IContentish

from kk.shopified.utils import get_cart
from kk.shopified.utils import wipe_cart
from kk.shopified.utils import format_price

from kk.shopified import MessageFactory as _


class ShoppingCartView(grok.View):
    grok.context(IContentish)
    grok.require('zope2.View')
    grok.name('cart')

    def update(self):
        context = aq_inner(self.context)
        self.context_url = context.absolute_url()
        self.uuid = IUUID(context, None)
        if 'form.button.Clear' in self.request:
            authenticator = getMultiAdapter((context, self.request),
                                            name=u"authenticator")
            if not authenticator.verify():
                raise Unauthorized
            wipe_cart()
            IStatusMessage(self.request).addStatusMessage(
                _(u"Your shopping cart has successfully been purged"),
                type="info")
            return self.request.response.redirect(self.context_url)
        if 'form.button.Submit' in self.request:
            self.errors = {}
            item = self.request.get('item.uuid', None)
            quantity = self.request.get('item.quantity', None)
            if quantity is None:
                self.errors['item.quantity'] = _(u"Quantity must be given")
            else:
                idx = 0
                updater = self.update_cart()  # implement this one
                cartitem = updater(item, quantity)
                if cartitem:
                    idx += 1
                    IStatusMessage(self.request).addStatusMessage(
                        _(u"%s cart items successfully updated") % idx,
                        type="info")
                redirect_url = self.context_url() + '/@@cart'
                return self.request.response.redirect(redirect_url)

    def cart(self):
        cart = get_cart()
        data = []
        for item in cart:
            info = {}
            product = uuidToObject(item)
            quantity = cart[item]
            info['uuid'] = item
            info['quantity'] = quantity
            info['title'] = product.Title()
            info['description'] = product.Description()
            info['url'] = product.absolute_url()
            info['price'] = format_price(product.price)
            total = quantity * int(product.price)
            info['price_total'] = format_price(total)
            data.append(info)
        return data

    def has_cart(self):
        cart = get_cart()
        return len(cart) > 0


class CartAddItem(grok.View):
    grok.context(IContentish)
    grok.require('zope2.View')
    grok.name('cart-add-item')

    def update(self):
        context = aq_inner(self.request)
        self.context_url = context.absolute_url()
        item = self.request.get('item.uuid', None)
        qty = self.request.get('quantity', None)
        IStatusMessage(self.request).addStatusMessage(
            _(u"Add item to cart executed: %s %s ") % (item, qty),
            type="info")
        import pdb; pdb.set_trace( )
        redirect_url = self.context_url() + '/@@cart'
        return self.request.response.redirect(redirect_url)

    def render(self):
        return ''


class CartRemoveItem(grok.View):
    grok.context(IContentish)
    grok.require('zope2.View')
    grok.name('cart-remove-item')

    def update(self):
        context = aq_inner(self.request)
        self.context_url = context.absolute_url()
        IStatusMessage(self.request).addStatusMessage(
            _(u"Remove item from cart executed. This is not yet implemented"),
            type="info")
        redirect_url = self.context_url() + '/@@cart'
        return self.request.response.redirect(redirect_url)

    def render(self):
        return ''


class CartClear(grok.View):
    grok.context(IContentish)
    grok.require('zope2.View')
    grok.name('cart-clear')

    def update(self):
        context = aq_inner(self.context)
        wipe_cart()
        self.context_url = context.absolute_url()
        IStatusMessage(self.request).addStatusMessage(
            _(u"Remove item from cart executed. This is not yet implemented"),
            type="info")
        redirect_url = self.context_url() + '/@@cart'
        return self.request.response.redirect(redirect_url)

    def render(self):
        return ''
