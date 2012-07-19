from five import grok
from Acquisition import aq_inner
from plone.directives import form

from zope import schema
from zope.component import getUtility
from zope.component import getMultiAdapter
from z3c.form import group, field, button

from plone.app.uuid.utils import uuidToObject

from plone.registry.interfaces import IRegistry
from plone.app.layout.navigation.interfaces import INavigationRoot
from Products.CMFCore.interfaces import IContentish

from kk.shopified.utils import get_cart
from kk.shopified.utils import format_price

from kk.shopified.interfaces import IShopifiedSettings

#registry = getUtility(IRegistry)
#settings = registry.forInterface(IAkismetSettings)

from kk.shopified import MessageFactory as _


class ICheckoutForm(form.Schema):
    """ Checkout form interface """


class CheckoutForm(form.Form):
    grok.context(INavigationRoot)
    grok.require('zope2.View')
    grok.name('checkout')

    schema = ICheckoutForm
    ignoreContext = True
    ignoreRequest = False
    css_class = 'overlayForm'

    label = _(u"Checkout")
    #description = _(u"Please fill out the form to send an enquiry.")

    enable_form_tabbing = False

    def update(self):
        # disable Plone's editable border
        self.request.set('disable_border', True)
        super(CheckoutForm, self).update()

    def updateActions(self):
        super(CheckoutForm, self).updateActions()
        self.actions["submit"].addClass("btn cta large")
        self.actions['cancel'].addClass("btn large")

    @button.buttonAndHandler(_(u'Send now'), name='submit')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        self.status = self.send_email(data)

    @button.buttonAndHandler(_(u'cancel'))
    def handleCancel(self, action):
        context = aq_inner(self.context)
        context_url = context.absolute_url()
        return self.request.response.redirect(context_url)


class CheckoutView(grok.View):
    grok.context(IContentish)
    grok.require('zope2.View')
    grok.name('check-out')

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
            info['image_tag'] = self.image_tag(product)
            info['url'] = product.absolute_url()
            info['price'] = product.price
            info['price_pretty'] = format_price(product.price)
            total = quantity * int(product.price)
            info['price_total'] = format_price(total)
            data.append(info)
        return data

    def has_cart(self):
        cart = get_cart()
        return len(cart) > 0

    def cart_total(self):
        total = 0.0
        for item in self.cart():
            value = item['price']
            value = value * int(item['quantity'])
            total = total + value
        return total

    def total_is_zero(self):
        return self.cart_total() <= 0

    def image_tag(self, obj):
        scales = getMultiAdapter((obj, self.request), name='images')
        scale = scales.scale('image', scale='thumb')
        imageTag = None
        if scale is not None:
            imageTag = scale.tag()
        return imageTag
