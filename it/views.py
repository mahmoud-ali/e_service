from django.shortcuts import render
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.html import format_html

from hr_bot.models import EmployeeTelegram
from it.forms import HelpRequestForm
from it.models import AccessPoint, EmployeeComputer, Peripheral #, NetworkAdapter
from it.utils import AI,queryset_to_markdown


class EmployeeComputerAskAIView(LoginRequiredMixin,DetailView):
    model = EmployeeComputer
    model_details = [Peripheral, AccessPoint] #NetworkAdapter,
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


class HelpdeskTelegramUser(DetailView):
    model = EmployeeComputer
    # template_name = "it/ai_prompt.html"

    def get(self,request,user_id):        
        employeeComputer = EmployeeComputer.objects.filter(id=user_id).first()
        form = HelpRequestForm()

        return render(request, "it/help_form.html", {"employee":employeeComputer.employee,"form": form})

    def post(self,request,user_id):        
        employeeComputer = EmployeeComputer.objects.filter(id=user_id).first()
        form = HelpRequestForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.employee = employeeComputer.employee
            obj.save()

            return render(request, "it/success.html")  # confirmation page
        
        return render(request, "it/help_form.html", {"form": form})
