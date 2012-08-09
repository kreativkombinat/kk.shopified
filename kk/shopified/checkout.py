import base64
import hashlib
import random
import urllib2
import cStringIO
import formatter
from htmllib import HTMLParser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.Header import Header

from five import grok
from Acquisition import aq_inner
from AccessControl import Unauthorized

from zope.component import getUtility
from zope.component import getMultiAdapter

from plone.app.uuid.utils import uuidToObject
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.registry.interfaces import IRegistry
from Products.CMFCore.interfaces import IContentish
from Products.statusmessages.interfaces import IStatusMessage

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
        unwanted = ('_authenticator', 'form.button.Submit',
                    'form.button.Enquiry')
        required = self.required_fields()
        if ('form.button.Submit' in self.request
            or 'form.button.Enquiry' in self.request):
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
            formdata['enquiry'] = self.request.get('form.button.Enquiry', None)
            if errorIdx > 0:
                self.errors = formerrors
            else:
                self._process_payment(formdata)

    def _process_payment(self, data):
        if data['enquiry'] is None:
            self._process_paypal(data)
        else:
            self._send_enquiry(data)

    def _process_paypal(self, data):
        pstate = getMultiAdapter((self.context, self.request),
                                  name=u"plone_portal_state")
        portal_url = pstate.portal_url()
        payment_settings = self._payment_settings()
        shop_url = payment_settings['shop_url']
        base_url = portal_url + shop_url
        txnid = self._generate_txn_id()
        txn_id = self._url_quote(txnid)
        return_url = base_url + '/@@payment-processed?oid=' + txn_id
        merchant_key = payment_settings['key']
        paypal_url = payment_settings['url']
        customername = data['fullname']
        name = customername.split(' ')
        fname = name[0:int(len(name) - 1)]
        firstname = ' '.join(fname)
        lastname = name[-1]
        shipping_costs = self._calculate_shipping(data['shipping.country'])
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
        if txn_item:
            self.context.REQUEST.RESPONSE.redirect(url)
            return 'SUCCESS'

    def _send_enquiry(self, data):
        pstate = getMultiAdapter((self.context, self.request),
                                  name=u"plone_portal_state")
        portal_url = pstate.portal_url()
        settings = self._payment_settings()
        txnid = self._generate_txn_id()
        txn_id = self._url_quote(txnid)
        shop_url = settings['shop_url']
        base_url = portal_url + shop_url
        success_url = base_url + '/@@payment-processed?oid=' + txn_id
        mto = settings['shop_email']
        envelope_from = data['email']
        fullname = safe_unicode(data['fullname'])
        subject = _(u'Poleworkx Shop: Anfrage von %s') % fullname
        options = data
        cart = self.cart()
        options['cartitems'] = cart
        country = data['shipping.country']
        shipping = self._calculate_shipping(country)
        net = self._calculate_cart_net(shipping)
        vat = self._calculate_cart_vat(net)
        options['cart_shipping'] = format_price(shipping)
        options['cart_vat'] = format_price(vat)
        options['cart_net'] = format_price(net)
        body = ViewPageTemplateFile("enquiry_email.pt")(self, **options)
        # send email
        mailhost = getToolByName(self.context, 'MailHost')
        mailhost.send(body, mto=mto, mfrom=envelope_from,
                      subject=subject, charset='utf-8')
        IStatusMessage(self.request).add(
            _(u"Your email has been forwarded."),
            type='info')
        txn_item = self._update_cart_on_checkout(txn_id)
        if txn_item:
            return self.request.response.redirect(success_url)

    def _update_cart_on_checkout(self, txn_id):
        updater = getUtility(ICartUpdaterUtility)
        for item in self.cart():
            updater.delete(item['uuid'])
        item = updater.mark(txn_id)
        return txn_id

    def _payment_settings(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IShopifiedSettings)
        processor = settings.paypal_url
        info = {}
        info['shop_url'] = settings.shop_url
        info['shop_email'] = settings.shop_email
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
                total = int(quantity) * product.price
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
            shipping = item['shipping']
            base_value = value + shipping
            value = base_value * int(item['quantity'])
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

    def _calculate_shipping(self, country):
        shipping = 0.0
        for item in self.cart():
            value = item['shipping']
            if value:
                shipping_value = value * int(item['quantity'])
                shipping = shipping + shipping_value
        if country in self.eu_countries():
            shipping = shipping + 10.0
        return shipping

    def _calculate_cart_net(self, shipping):
        total = self.cart_total()
        net = total + shipping
        return net

    def _calculate_cart_vat(self, net):
        vat = net * 0.19
        return vat

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
        key = base64.b64encode(
                hashlib.sha256(str(random.getrandbits(256))
                ).digest(), random.choice([
                'rA', 'aZ', 'gQ', 'hH', 'hG', 'aR', 'DD'])).rstrip('==')
        return key

    def create_plaintext_message(self, text):
        """ Create a plain-text-message by parsing the html
            and attaching links as endnotes
        """
        plain_text_maxcols = 72
        textout = cStringIO.StringIO()
        formtext = formatter.AbstractFormatter(formatter.DumbWriter(
                        textout, plain_text_maxcols))
        parser = HTMLParser(formtext)
        parser.feed(text)
        parser.close()
        # append the anchorlist at the bottom of a message
        # to keep the message readable.
        counter = 0
        anchorlist = "\n\n" + ("-" * plain_text_maxcols) + "\n\n"
        for item in parser.anchorlist:
            counter += 1
            if item.startswith('https://'):
                new_item = item.replace('https://', 'http://')
            else:
                new_item = item
            anchorlist += "[%d] %s\n" % (counter, new_item)
        text = textout.getvalue() + anchorlist
        del textout, formtext, parser, anchorlist
        return text

    def default_value(self, error):
        value = ''
        if error['active'] == False:
            value = error['msg']
        return value

    def image_tag(self, obj):
        scales = getMultiAdapter((obj, self.request), name='images')
        scale = scales.scale('image', scale='thumb')
        imageTag = None
        if scale is not None:
            imageTag = scale.tag()
        return imageTag

    def required_fields(self):
        fields = ('fullname', 'email', 'shipping.city', 'shipping.zipcode',
                  'shipping.address_1', 'shipping.country')
        return fields

    def eu_countries(self):
        countries = ('Belgium', 'Bulgaria', 'Czech Republic', 'Denmark',
        'Estonia', 'Ireland', 'Greece', 'Spain', 'France', 'Italy', 'Cyprus',
        'Latvia', 'Lithuania', 'Luxembourg', 'Hungary', 'Malta', 'Netherlands',
        'Austria', 'Poland', 'Portugal', 'Romania', 'Slovenia', 'Slovakia',
        'Finland', 'Sweden', 'United Kingdom')
        return countries
