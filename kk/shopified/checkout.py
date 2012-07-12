from five import grok
from Acquisition import aq_inner
from plone.directives import form

from zope import schema
from zope.component import getUtility
from z3c.form import group, field, button

from plone.registry.interfaces import IRegistry
from plone.app.layout.navigation.interfaces import INavigationRoot

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
