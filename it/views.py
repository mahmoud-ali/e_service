from django.shortcuts import render
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.html import format_html

from it.models import AccessPoint, EmployeeComputer, NetworkAdapter, Peripheral
from it.utils import AI,queryset_to_markdown


class EmployeeComputerAskAIView(LoginRequiredMixin,DetailView):
    model = EmployeeComputer
    model_details = [NetworkAdapter, Peripheral, AccessPoint]
    template_name = "it/ai_prompt.html"

    def get(self,request,pk):        
        obj = self.get_object()

        user_setup = []
        for model in self.model_details:
            qs = model.objects.filter(computer=obj.computer)
            if qs.count() > 0:
                user_setup.append({
                    "title":"## "+qs[0]._meta.verbose_name,
                    "md": format_html(queryset_to_markdown(qs,["id","computer"]))
                })

        prompt = AI.get("prompt")
        
        network_setup = AI.get("network_setup")
        
        faq = AI.get("faq")

        self.extra_context = {
            "prompt":prompt,
            "faq":faq, 
            "network_setup":network_setup, 
            "user_setup":user_setup, 
         }

        return render(request, self.template_name, self.extra_context)
