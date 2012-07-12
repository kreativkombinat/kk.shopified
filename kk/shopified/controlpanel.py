from plone.app.registry.browser import controlpanel

from kk.shopified.interfaces import IShopifiedSettings

from kk.shopified import MessageFactory as _


class ShopifiedSettingsEditForm(controlpanel.RegistryEditForm):

    schema = IShopifiedSettings
    label = _(u"Shopified settings")
    description = _(u"""""")

    def updateFields(self):
        super(ShopifiedSettingsEditForm, self).updateFields()

    def updateWidgets(self):
        super(ShopifiedSettingsEditForm, self).updateWidgets()


class ShopifiedSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = ShopifiedSettingsEditForm
