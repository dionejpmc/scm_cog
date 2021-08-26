from django.views.generic import TemplateView


class HomePageView(TemplateView):
    template_name = "home.html"

class MenuPageView(TemplateView):
    template_name = "menu/menu_inicio.html"