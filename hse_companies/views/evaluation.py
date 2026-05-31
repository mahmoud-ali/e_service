from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from hse_companies.models import (
    TblCompanyEvaluationSession,
    TblCompanyEvaluationEnvironment,
    TblCompanyEvaluationSafety,
    TblCompanyEvaluationGeneral
)
from hse_companies.forms import (
    HseEvaluationSessionForm,
    HseEnvironmentEvaluationForm,
    HseSafetyEvaluationForm,
    HseGeneralEvaluationForm
)

class EvaluationSessionListView(LoginRequiredMixin, ListView):
    model = TblCompanyEvaluationSession
    template_name = 'hse_companies/evaluation/session_list.html'
    context_object_name = 'sessions'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("قائمة تقييمات الشركات (HSE)")
        context['env_count'] = TblCompanyEvaluationSession.objects.filter(environment__isnull=False).count()
        context['safe_count'] = TblCompanyEvaluationSession.objects.filter(safety__isnull=False).count()
        context['gen_count'] = TblCompanyEvaluationSession.objects.filter(general__isnull=False).count()
        return context

class EvaluationSessionCreateView(LoginRequiredMixin, CreateView):
    model = TblCompanyEvaluationSession
    form_class = HseEvaluationSessionForm
    template_name = 'hse_companies/evaluation/session_form.html'
    success_url = reverse_lazy('hse_companies:evaluation_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['env_form'] = HseEnvironmentEvaluationForm(self.request.POST, prefix='env')
            context['safe_form'] = HseSafetyEvaluationForm(self.request.POST, prefix='safe')
            context['gen_form'] = HseGeneralEvaluationForm(self.request.POST, prefix='gen')
        else:
            context['env_form'] = HseEnvironmentEvaluationForm(prefix='env')
            context['safe_form'] = HseSafetyEvaluationForm(prefix='safe')
            context['gen_form'] = HseGeneralEvaluationForm(prefix='gen')
        context['title'] = _("تقييم جديد لبيئة وسلامة شركة")
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        env_form = context['env_form']
        safe_form = context['safe_form']
        gen_form = context['gen_form']

        if form.is_valid() and env_form.is_valid() and safe_form.is_valid() and gen_form.is_valid():
            session = form.save(commit=False)
            session.created_by = self.request.user
            session.updated_by = self.request.user
            session.save()

            env = env_form.save(commit=False)
            env.session = session
            env.created_by = self.request.user
            env.updated_by = self.request.user
            env.save()

            safe = safe_form.save(commit=False)
            safe.session = session
            safe.created_by = self.request.user
            safe.updated_by = self.request.user
            safe.save()

            gen = gen_form.save(commit=False)
            gen.session = session
            gen.created_by = self.request.user
            gen.updated_by = self.request.user
            gen.save()

            messages.success(self.request, _("تم حفظ التقييم بجميع محاوره بنجاح."))
            return super().form_valid(form)
        else:
            messages.error(self.request, _("يرجى مراجعة الأخطاء في الاستمارة."))
            return self.render_to_response(self.get_context_data(form=form))

class EvaluationSessionUpdateView(LoginRequiredMixin, UpdateView):
    model = TblCompanyEvaluationSession
    form_class = HseEvaluationSessionForm
    template_name = 'hse_companies/evaluation/session_form.html'
    success_url = reverse_lazy('hse_companies:evaluation_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['env_form'] = HseEnvironmentEvaluationForm(self.request.POST, prefix='env', instance=getattr(self.object, 'environment', None))
            context['safe_form'] = HseSafetyEvaluationForm(self.request.POST, prefix='safe', instance=getattr(self.object, 'safety', None))
            context['gen_form'] = HseGeneralEvaluationForm(self.request.POST, prefix='gen', instance=getattr(self.object, 'general', None))
        else:
            context['env_form'] = HseEnvironmentEvaluationForm(prefix='env', instance=getattr(self.object, 'environment', None))
            context['safe_form'] = HseSafetyEvaluationForm(prefix='safe', instance=getattr(self.object, 'safety', None))
            context['gen_form'] = HseGeneralEvaluationForm(prefix='gen', instance=getattr(self.object, 'general', None))
        context['title'] = _("تحديث تقييم الشركة")
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        env_form = context['env_form']
        safe_form = context['safe_form']
        gen_form = context['gen_form']

        if form.is_valid() and env_form.is_valid() and safe_form.is_valid() and gen_form.is_valid():
            session = form.save(commit=False)
            session.updated_by = self.request.user
            session.save()

            env = env_form.save(commit=False)
            env.session = session
            env.updated_by = self.request.user
            env.save()

            safe = safe_form.save(commit=False)
            safe.session = session
            safe.updated_by = self.request.user
            safe.save()

            gen = gen_form.save(commit=False)
            gen.session = session
            gen.updated_by = self.request.user
            gen.save()

            messages.success(self.request, _("تم تحديث التقييم بجميع محاوره بنجاح."))
            return super().form_valid(form)
        else:
            messages.error(self.request, _("يرجى مراجعة الأخطاء في الاستمارة."))
            return self.render_to_response(self.get_context_data(form=form))

class EvaluationSessionDetailView(LoginRequiredMixin, DetailView):
    model = TblCompanyEvaluationSession
    template_name = 'hse_companies/evaluation/session_detail.html'
    context_object_name = 'session'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = self.get_object()
        
        # Helper function to get fields data
        def get_fields_data(evaluation_obj, prefix):
            fields_data = []
            if not evaluation_obj: return fields_data
            for field in evaluation_obj._meta.fields:
                if field.name.startswith(prefix):
                    val = getattr(evaluation_obj, field.name)
                    choices_dict = dict(field.choices)
                    fields_data.append({
                        'name': field.name,
                        'label': field.verbose_name,
                        'value': val,
                        'value_display': choices_dict.get(val, val)
                    })
            return fields_data

        context['env_fields'] = get_fields_data(getattr(session, 'environment', None), 'env_')
        context['safe_fields'] = get_fields_data(getattr(session, 'safety', None), 'safe_')
        context['gen_fields'] = get_fields_data(getattr(session, 'general', None), 'gen_')
        
        context['env_avg'] = session.environment.get_average_score() if getattr(session, 'environment', None) else 0
        context['safe_avg'] = session.safety.get_average_score() if getattr(session, 'safety', None) else 0
        context['gen_avg'] = session.general.get_average_score() if getattr(session, 'general', None) else 0
        
        context['title'] = _("تفاصيل التقييم الشامل للشركة")
        return context
