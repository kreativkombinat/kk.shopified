from zope.component import getUtility
from zope.site.hooks import getSite
from zope.globalrequest import getRequest
from collective.beaker.interfaces import ISession

from kk.shopified.interfaces import IShoppingCartUtility


def format_price(price):
    if price < 0:
        return '-%0.2f EUR' % abs(price)
    else:
        return '%0.2f EUR' % price


def get_cart():
    return getUtility(IShoppingCartUtility).get(getSite())


def wipe_cart():
    return getUtility(IShoppingCartUtility).destroy(getSite())


def update_cart():
    return getUtility(IShoppingCartUtility).update(getSite())


def redirect_to_checkout():
    site = getSite()
    request = getRequest()
    session = ISession(request)
    session.save()
    request.response.redirect(site.absolute_url() + '/@@checkout')
