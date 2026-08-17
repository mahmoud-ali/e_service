from datetime import date
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from hse_companies.models import AppHSECorrectiveAction, AppHSEPerformanceReport
from hse_companies.models.incidents import IncidentInfo
from company_profile.models import TblCompanyProduction

class CorrectiveActionReportPDFView(LoginRequiredMixin, TemplateView):
    template_name = "hse_companies/corrective_action_report.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        report_id = kwargs.get('report_id')
        action_id = kwargs.get('action_id')
        incident_id = kwargs.get('incident_id')
        company_id = kwargs.get('company_id')

        actions = []
        company = None
        visit_date = None

        if action_id:
            action = get_object_or_404(AppHSECorrectiveAction, pk=action_id)
            actions = [action]
            if action.report:
                company = action.report.company
                visit_date = action.report.created_at
            elif action.incident:
                company = action.incident.company
                visit_date = getattr(action.incident, 'incident_date', None) or getattr(action.incident, 'created_at', None)

        elif report_id:
            report = get_object_or_404(AppHSEPerformanceReport, pk=report_id)
            actions = AppHSECorrectiveAction.objects.filter(report=report).order_by('id')
            company = report.company
            visit_date = report.created_at

        elif incident_id:
            incident = get_object_or_404(IncidentInfo, pk=incident_id)
            actions = AppHSECorrectiveAction.objects.filter(incident=incident).order_by('id')
            company = incident.company
            visit_date = getattr(incident, 'incident_date', None) or getattr(incident, 'created_at', None)

        elif company_id:
            company = get_object_or_404(TblCompanyProduction, pk=company_id)
            actions = AppHSECorrectiveAction.objects.filter(
                Q(report__company=company) | Q(incident__company=company)
            ).order_by('-id')
            if actions.exists():
                first_act = actions.first()
                if first_act.report:
                    visit_date = first_act.report.created_at
                elif first_act.incident:
                    visit_date = getattr(first_act.incident, 'incident_date', None) or getattr(first_act.incident, 'created_at', None)

        else:
            # Fallback for selected IDs via GET query params ?ids=1,2,3 or POST
            req_ids = self.request.GET.get('ids')
            if req_ids:
                id_list = [int(i) for i in req_ids.split(',') if i.isdigit()]
                actions = AppHSECorrectiveAction.objects.filter(id__in=id_list).order_by('id')
                if actions.exists():
                    for act in actions:
                        if act.report and act.report.company:
                            company = act.report.company
                            visit_date = act.report.created_at
                            break
                        elif act.incident and act.incident.company:
                            company = act.incident.company
                            visit_date = getattr(act.incident, 'incident_date', None) or getattr(act.incident, 'created_at', None)
                            break

        context['actions'] = actions
        context['company'] = company
        context['visit_date'] = visit_date
        context['report_date'] = date.today()
        ref_id = report_id or action_id or incident_id or company_id or 'merged'
        context['report_ref'] = f"HSE-CA-{ref_id}"
        return context
