from django.views.generic import TemplateView
from django.shortcuts import render


class AboutPageView(TemplateView):
    template_name = 'pages/about.html'


class RulesPageView(TemplateView):
    template_name = 'pages/rules.html'


# Обработчики ошибок остаются функциями
def handler403_csrf(request, exception=None):
    return render(request, 'pages/403csrf.html', status=403)


def handler404(request, exception):
    return render(request, 'pages/404.html', status=404)


def handler500(request):
    return render(request, 'pages/500.html', status=500)
