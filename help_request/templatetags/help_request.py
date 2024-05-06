from django import template
from django.template.loader import get_template
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe

from help_request.forms import HelpForm

register = template.Library()

@register.simple_tag
def help_link(*args, **kwargs):
    app_name =  args[0];
    link_txt = _("help_link")
    link = f'<a href="#" type="button" class="btn btn-link btn" data-toggle="modal" data-target="#helpRequest{app_name}"> \
            {link_txt} \
            </a>'
    
    return mark_safe(link)

@register.simple_tag
def help_model(*args, **kwargs):
    template_name = 'help_request/model.html'
    context = {
        "html2canvas_lib":"https://html2canvas.hertzen.com/dist/html2canvas.min.js",
        "dom_selector":"div.main",
        "form":HelpForm,
        "app_name": args[0],
    }

    template = get_template(template_name)
    return template.render(context)
