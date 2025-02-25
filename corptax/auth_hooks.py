from allianceauth import hooks
from allianceauth.services.hooks import MenuItemHook, UrlHook

from . import urls


class CorptaxMenuItem(MenuItemHook):
    """ This class ensures only authorized users will see the menu entry """

    def __init__(self):
        # setup menu entry for sidebar
        MenuItemHook.__init__(
            self,
            "Corptax",
            "fas fa-cube fa-fw",
            "corptax:index",
            navactive=["corptax:"],
        )

    def render(self, request):
        if request.user.has_perm("corptax.basic_access"):
            return MenuItemHook.render(self, request)
        return ""


@hooks.register("menu_item_hook")
def register_menu():
    return CorptaxMenuItem()


@hooks.register("url_hook")
def register_urls():
    return UrlHook(urls, "corptax", r"^corptax/")
