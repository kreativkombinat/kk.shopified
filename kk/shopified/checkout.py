import os
import base64
import urllib2
from five import grok
from Acquisition import aq_inner
from AccessControl import Unauthorized

from zope.component import getUtility
from zope.component import getMultiAdapter

from plone.app.uuid.utils import uuidToObject

from plone.registry.interfaces import IRegistry
from Products.CMFCore.interfaces import IContentish

from kk.shopified.utils import get_cart
from kk.shopified.utils import format_price

from kk.shopified.interfaces import IShopifiedSettings
from kk.shopified.interfaces import ICartUpdaterUtility

from kk.shopified import MessageFactory as _


class CheckoutView(grok.View):
    grok.context(IContentish)
    grok.require('zope2.View')
    grok.name('checkout')

    def update(self):
        context = aq_inner(self.context)
        self.errors = {}
        unwanted = ('_authenticator', 'form.button.Submit')
        required = self.required_fields()
        if 'form.button.Submit' in self.request:
            form = self.request.form
            authenticator = getMultiAdapter((context, self.request),
                                            name=u"authenticator")
            if not authenticator.verify():
                raise Unauthorized
            formdata = {}
            formerrors = {}
            errorIdx = 0
            for value in form:
                if value not in unwanted:
                    formdata[value] = form[value]
                    if value in required and not form[value]:
                        error = {}
                        error['active'] = True
                        error['msg'] = _(u"This field is required")
                        formerrors[value] = error
                        errorIdx += 1
                    else:
                        error = {}
                        error['active'] = False
                        error['msg'] = form[value]
                        formerrors[value] = error
            if errorIdx > 0:
                self.errors = formerrors
            else:
                self._process_payment(formdata)

    def _process_payment(self, data):
        pstate = getMultiAdapter((self.context, self.request),
                                  name=u"plone_portal_state")
        portal_url = pstate.portal_url()
        payment_settings = self._payment_settings()
        txn_id = self._generate_txn_id()
        shop_url = payment_settings['shop_url']
        base_url = portal_url + shop_url
        return_url = base_url + '/@@payment-processed?oid=' + txn_id
        merchant_key = payment_settings['key']
        paypal_url = payment_settings['url']
        customername = data['fullname']
        name = customername.split(' ')
        fname = name[0:int(len(name) - 1)]
        firstname = ' '.join(fname)
        lastname = name[-1]
        shipping_costs = self.cart_shipping()
        info = {"cmd": "_cart",
                "upload": "1",
                "business": merchant_key,
                "currency_code": "EUR",
                #"notify_url": notify_url,
                "return": return_url,
                "lc": "DE",
                "charset": "utf-8",
                "first_name": self._url_quote(firstname),
                "last_name": self._url_quote(lastname),
                "address1": self._url_quote(data['shipping.address1']),
                "address2": self._url_quote(data['shipping.address2']),
                "city": self._url_quote(data['shipping.city']),
                "country": self._url_quote(data['shipping.country']),
                "zip": data['shipping.zipcode'],
                "shipping_1": shipping_costs
                }
        cart = self.cart()
        for i, item in enumerate(cart):
            j = i + 1
            name = "item_name_%s" % j
            quantity = "quantity_%s" % j
            amount = "amount_%s" % j
            info[name] = self._url_quote(item['title'])
            info[quantity] = item['quantity']
            info[amount] = item['price']
        parameters = "&".join(["%s=%s" % (k, v) for (k, v) in info.items()])
        url = paypal_url + "?" + parameters
        txn_item = self._update_cart_on_checkout(txn_id)
        import pdb; pdb.set_trace( )
        if txn_item:
            self.context.request.response.redirect(url)
            return 'SUCCESS'

    def _update_cart_on_checkout(self, txn_id):
        updater = getUtility(ICartUpdaterUtility)
        item = updater.mark(txn_id)
        return item

    def _payment_settings(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IShopifiedSettings)
        processor = settings.paypal_url
        info = {}
        info['shop_url'] = settings.shop_url
        if processor == 'Sandbox':
            info['key'] = settings.paypal_sandbox
            info['url'] = 'https://www.sandbox.paypal.com/cgi-bin/webscr'
        else:
            info['key'] = settings.paypal_key
            info['url'] = 'https://www.paypal.com/cgi-bin/webscr'
        return info

    def cart(self):
        cart = get_cart()
        data = []
        for item in cart:
            if item != 'txn_id':
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
                info['shipping'] = product.shipping_price
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

    def cart_net(self):
        return format_price(self.cart_total())

    def cart_vat(self):
        total = self.cart_total()
        vat = total * 0.19
        return format_price(vat)

    def cart_shipping(self):
        shipping = 0.0
        for item in self.cart():
            value = item['shipping']
            if value:
                shipping_value = value * int(item['quantity'])
                shipping = shipping + shipping_value
            return format_price(shipping)

    def image_tag(self, obj):
        scales = getMultiAdapter((obj, self.request), name='images')
        scale = scales.scale('image', scale='thumb')
        imageTag = None
        if scale is not None:
            imageTag = scale.tag()
        return imageTag

    def _url_quote(self, value):
        if value:
            try:
                encoded_value = urllib2.quote(value.encode('utf-8'))
            except:
                encoded_value = urllib2.quote(value)
            return encoded_value
        else:
            return ''

    def _generate_txn_id(self):
        return base64.b64encode(os.urandom(24))

    def default_value(self, error):
        value = ''
        if error['active'] == False:
            value = error['msg']
        return value

    def required_fields(self):
        fields = ('fullname', 'email', 'phone',
                  'shipping.city', 'shipping.zipcode',
                  'shipping.address_1', 'shipping.address_2',
                  'shipping.country')
        return fields

    def eu_countries(self):
        countries = ('Belgium', 'Bulgaria', 'Czech Republic', 'Denmark',
        'Estonia', 'Ireland', 'Greece', 'Spain', 'France', 'Italy', 'Cyprus',
        'Latvia', 'Lithuania', 'Luxembourg', 'Hungary', 'Malta', 'Netherlands',
        'Austria', 'Poland', 'Portugal', 'Romania', 'Slovenia', 'Slovakia',
        'Finland', 'Sweden', 'United Kingdom')
        return countries
