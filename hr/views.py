import csv
import codecs
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import View
from django.utils.translation import gettext_lazy as _
from django.utils import cache
from django.views.defaults import bad_request
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from hr.models import Drajat3lawat, EmployeeBankAccount, EmployeeBasic, PayrollDetail, PayrollMaster,MONTH_CHOICES
from hr.payroll import M2moriaSheet, MobasharaSheet, Payroll,Mokaf2Sheet

SHOW_CSV_TOTAL = False

def get_employee_accounts():
    data = {}
    for emp in EmployeeBankAccount.objects.filter(active=True).prefetch_related("employee"):
        id = emp.employee.id
        data[id] = (emp.account_no,emp.get_bank_display())
        # print(f'id: {id}, account_no: {data[id]}')

    return data

class UserPermissionMixin(UserPassesTestMixin):
    user_groups = []

    def test_func(self):
        return self.request.user.groups.filter(name__in=self.user_groups).exists()

class Badalat(LoginRequiredMixin,UserPermissionMixin,View):
    user_groups = ['hr_manager','hr_payroll']
    def get(self,*args,**kwargs):
        year = self.request.GET['year']
        month = int(self.request.GET['month'])
        format = self.request.GET.get('format',None)
        data = []
        
        payroll = Payroll(year,month)
        header = ['الرمز','الموظف','الدرجة الوظيفية','العلاوة','ابتدائي','غلاء معيشة','اساسي','طبيعة عمل','تمثيل','مهنة','معادن','مخاطر','عدوى','اجتماعية قسيمة','اجتماعية اطفال','مؤهل','شخصية','اجمالي المرتب']
        summary_list = []

        for (emp,badalat,khosomat,draja_wazifia,alawa_sanawia) in payroll.all_employees_payroll_from_db():
            badalat_list = [round(b[1],2) for b in badalat]
            l = [emp.code,emp.name,Drajat3lawat.DRAJAT_CHOICES[draja_wazifia],Drajat3lawat.ALAWAT_CHOICES[alawa_sanawia]] + badalat_list
            data.append(l)

            for idx,s in enumerate(badalat_list):
                try:
                    summary_list[idx] += badalat_list[idx]
                except IndexError:
                    summary_list.insert(idx,badalat_list[idx])

        summary_list = [round(s,2) for s in summary_list]

        if format == 'csv':
            sheet_name = 'allowances'
            response = HttpResponse(
                content_type="text/csv",
                headers={"Content-Disposition": f'attachment; filename="{sheet_name}_{month}_{year}.csv"'},
            )

            # BOM
            response.write(codecs.BOM_UTF8)

            writer = csv.writer(response)
            writer.writerow(header)

            if SHOW_CSV_TOTAL:
                data.append(['-','-','-','-',]+summary_list)

            for r in data:
                writer.writerow(r)

            cache.patch_cache_control(response, max_age=0)
            return response

        else:
            template_name = 'hr/badalat.html'
            context = {
                'title':'كشف بدلات',
                'header':header,
                'data': data,
                'summary':summary_list,
                'month':MONTH_CHOICES[month],
                'year':year,
            }

            response = render(self.request,template_name,context)
            cache.patch_cache_control(response, max_age=0)
            return response
    
class Khosomat(LoginRequiredMixin,UserPermissionMixin,View):
    user_groups = ['hr_manager','hr_payroll']
    def get(self,*args,**kwargs):
        year = self.request.GET['year']
        month = int(self.request.GET['month'])
        format = self.request.GET.get('format',None)
        bank_sheet = self.request.GET.get('bank_sheet',False)
        data = []
        payroll_master = None

        try:
            payroll_master = PayrollMaster.objects.get(year=year,month=month)
        except PayrollMaster.DoesNotExist as e:
            bad_request(self.request,e)
        
        payroll = Payroll(year,month)

        header = ['الرمز','الموظف','الدرجة الوظيفية','العلاوة','تأمين اجتماعي','معاش','الصندوق','الضريبة','دمغه','إجمالي الإستقطاعات الأساسية',]

        if payroll_master.enable_sandog_kahraba:
            header += ['صندوق كهربائيه',]

        header += ['السلفيات',]

        if payroll_master.enable_youm_algoat_almosalaha:
            header += ['استقطاع القوات المسلحه',]

        header += ['الزكاة','سلفيات الصندوق','إجمالي الإستقطاعات السنوية','خصومات - جزاءات','إجمالي الإستقطاع الكلي','صافي الإستحقاق']

        summary_list = []

        if bank_sheet:
            template_name = 'hr/bank.html'
            header = ['الرمز','الموظف','البنك','رقم الحساب','صافي الاستحقاق']
            emp_accounts = get_employee_accounts()

            for (emp,badalat,khosomat,draja_wazifia,alawa_sanawia) in payroll.all_employees_payroll_from_db():
                try:
                    bnk_no,bank = emp_accounts[emp.id] #employeeemp.employeebankaccount_set.get(active=True).account_no
                except KeyError:
                    bnk_no,bank = ('-','-')

                l = [emp.code,emp.name,bank,bnk_no,round(khosomat.safi_alisti7gag,2)]
                data.append(l)
        else:
            template_name = 'hr/khosomat.html'

            for (emp,badalat,khosomat,draja_wazifia,alawa_sanawia) in payroll.all_employees_payroll_from_db():
                khosomat_list = [round(k[1],2) for k in khosomat]
                l = [emp.code,emp.name,Drajat3lawat.DRAJAT_CHOICES[draja_wazifia],Drajat3lawat.ALAWAT_CHOICES[alawa_sanawia]] + khosomat_list
                data.append(l)

                for idx,s in enumerate(khosomat_list):
                    try:
                        summary_list[idx] += khosomat_list[idx]
                    except IndexError:
                        summary_list.insert(idx,khosomat_list[idx])

            summary_list = [round(s,2) for s in summary_list]

        if format == 'csv':
            sheet_name = 'net'
            # print(f'attachment; filename="{sheet_name}_{month}_{year}.csv"')
            response = HttpResponse(
                content_type="text/csv",
                headers={"Content-Disposition": f'attachment; filename="{sheet_name}_{month}_{year}.csv"'},
            )

            # BOM
            response.write(codecs.BOM_UTF8)

            writer = csv.writer(response)
            writer.writerow(header)

            if SHOW_CSV_TOTAL:
                data.append(['-','-','-','-',]+summary_list)

            for r in data:
                writer.writerow(r)

            cache.patch_cache_control(response, max_age=0)
            return response

        else:
            context = {
                'title':'كشف استقطاعات',
                'header':header,
                'data': data,
                'summary':summary_list,
                'month':MONTH_CHOICES[month],
                'year':year,
            }

            response = render(self.request,template_name,context)
            cache.patch_cache_control(response, max_age=0)
            return response
        
def cmp_drjat(draja,old_draja):
    if draja == old_draja:
        return Drajat3lawat.DRAJAT_CHOICES[draja]
    
    draja_str = 'لايوجد'
    if draja:
        draja_str = Drajat3lawat.DRAJAT_CHOICES[draja]

    old_draja_str = 'لايوجد'
    if old_draja:
        old_draja_str = Drajat3lawat.DRAJAT_CHOICES[old_draja]

    return old_draja_str + ' / ' + draja_str

def cmp_alawa(alawa,old_alawa):
    if alawa == old_alawa:
        return Drajat3lawat.ALAWAT_CHOICES[alawa]

    alawa_str = 'لايوجد'
    if alawa:
        alawa_str = Drajat3lawat.ALAWAT_CHOICES[alawa]

    old_alawa_str = 'لايوجد'
    if old_alawa:
        old_alawa_str = Drajat3lawat.ALAWAT_CHOICES[old_alawa]

    return old_alawa_str + ' / ' + alawa_str

class FargBadalat(LoginRequiredMixin,UserPermissionMixin,View):
    user_groups = ['hr_manager','hr_payroll']
    def get(self,*args,**kwargs):
        year = self.request.GET['year']
        month = int(self.request.GET['month'])
        format = self.request.GET.get('format',None)
        data = []
        
        payroll = Payroll(year,month)
        header = ['الرمز','الموظف','الدرجة الوظيفية','العلاوة','ابتدائي','غلاء معيشة','اساسي','طبيعة عمل','تمثيل','مهنة','معادن','مخاطر','عدوى','اجتماعية قسيمة','اجتماعية اطفال','مؤهل','شخصية','اجمالي المرتب']
        summary_list = []

        cmp_year = self.request.GET['cmp_year']
        cmp_month = self.request.GET['cmp_month']
        cmp_payroll = Payroll(cmp_year,cmp_month)
        cmp_index = {}
        emp_lst = []

        for d in cmp_payroll.all_employees_payroll_from_db():
            cmp_index.update({d[0].id:d})

        for (emp,badalat,khosomat,draja_wazifia,alawa_sanawia) in payroll.all_employees_payroll_from_db():
            emp_lst.append(emp.id)
            cmp_draja_wazifia = cmp_alawa_sanawia = None
            try:
                cmp_emp,cmp_badalat,cmp_khosomat,cmp_draja_wazifia,cmp_alawa_sanawia = cmp_index[emp.id] #cmp_payroll.employee_payroll_from_employee(emp)
                badalat_list = [round((zp[0][1]-zp[1][1]),2) for zp in zip(badalat,cmp_badalat)]
            except KeyError:
                badalat_list = [round(zp[1],2) for zp in badalat]
            
            if abs(sum(badalat_list)) > 0:
                l = [
                    emp.code,
                    emp.name,
                    cmp_drjat(draja_wazifia,cmp_draja_wazifia),
                    cmp_alawa(alawa_sanawia,cmp_alawa_sanawia),
                ] + badalat_list
                data.append(l)

                for idx,s in enumerate(badalat_list):
                    try:
                        summary_list[idx] += badalat_list[idx]
                    except IndexError:
                        summary_list.insert(idx,badalat_list[idx])

        #employees not exists in first sheet
        for payroll_detail in PayrollDetail.objects.filter(payroll_master=cmp_payroll.payroll_master).exclude(employee__in=emp_lst):
            cmp_emp,cmp_badalat,cmp_khosomat,cmp_draja_wazifia,cmp_alawa_sanawia = cmp_payroll.employee_payroll_from_employee(payroll_detail.employee)
            badalat_list = [round(-zp[1],2) for zp in cmp_badalat]
            
            if abs(sum(badalat_list)) > 0:
                l = [
                    cmp_emp.code,
                    cmp_emp.name,
                    cmp_drjat(None,cmp_draja_wazifia),
                    cmp_alawa(None,cmp_alawa_sanawia),
                ] + badalat_list
                data.append(l)

                for idx,s in enumerate(badalat_list):
                    try:
                        summary_list[idx] += badalat_list[idx]
                    except IndexError:
                        summary_list.insert(idx,badalat_list[idx])

        summary_list = [round(s,2) for s in summary_list]

        if format == 'csv':
            sheet_name = 'diff_allowances'
            response = HttpResponse(
                content_type="text/csv",
                headers={"Content-Disposition": f'attachment; filename="{sheet_name}_{month}_{year}.csv"'},
            )

            # BOM
            response.write(codecs.BOM_UTF8)

            writer = csv.writer(response)
            writer.writerow(header)

            if SHOW_CSV_TOTAL:
                data.append(['-','-','-','-',]+summary_list)

            for r in data:
                writer.writerow(r)

            cache.patch_cache_control(response, max_age=0)
            return response

        else:
            template_name = 'hr/badalat.html'
            context = {
                'title':'كشف فروقات بدلات',
                'header':header,
                'data': data,
                'summary':summary_list,
                'month':MONTH_CHOICES[month],
                'year':year,
            }

            response = render(self.request,template_name,context)
            cache.patch_cache_control(response, max_age=0)
            return response

def get_bank_display(key):
    if not key:
        return ''
    return EmployeeBankAccount.BANK_CHOICES[key]

class FargKhosomat(LoginRequiredMixin,UserPermissionMixin,View):
    user_groups = ['hr_manager','hr_payroll']
    def get(self,*args,**kwargs):
        year = self.request.GET['year']
        month = int(self.request.GET['month'])
        format = self.request.GET.get('format',None)
        bank_sheet = self.request.GET.get('bank_sheet',False)
        data = []
        payroll_master = None

        cmp_year = self.request.GET['cmp_year']
        cmp_month = self.request.GET['cmp_month']
        cmp_payroll = Payroll(cmp_year,cmp_month)
        cmp_index = {}
        emp_lst = []

        try:
            payroll_master = PayrollMaster.objects.get(year=year,month=month)
        except PayrollMaster.DoesNotExist as e:
            bad_request(self.request,e)
        
        payroll = Payroll(year,month)

        header = ['الرمز','الموظف','الدرجة الوظيفية','العلاوة','تأمين اجتماعي','معاش','الصندوق','الضريبة','دمغه','إجمالي الإستقطاعات الأساسية',]

        if payroll_master.enable_sandog_kahraba:
            header += ['صندوق كهربائيه',]

        header += ['السلفيات',]

        if payroll_master.khasm_salafiat_elsandog_min_elomoratab:
            header += ['سلفيات الصندوق',]

        if payroll_master.enable_youm_algoat_almosalaha:
            header += ['استقطاع القوات المسلحه',]

        header += ['الزكاة','سلفيات الصندوق','إجمالي الإستقطاعات السنوية','خصومات - جزاءات','إجمالي الإستقطاع الكلي','صافي الإستحقاق']

        summary_list = []

        for d in cmp_payroll.all_employees_payroll_from_db_with_bank_account():
            cmp_index.update({d[0].id:d})

        if bank_sheet:
            template_name = 'hr/bank.html'
            header = ['الرمز','الموظف','البنك','رقم الحساب']

            for (emp,badalat,khosomat,draja_wazifia,alawa_sanawia,bank,account_no) in payroll.all_employees_payroll_from_db_with_bank_account():
                if not account_no:
                    account_no = ''
                try:
                    (*rest,cmp_bank,cmp_account_no) = cmp_index[emp.id]
                    if not cmp_account_no:
                        cmp_account_no = ''

                except KeyError:
                    (cmp_bank,cmp_account_no) = ('','')

                if(cmp_account_no != account_no):
                    l = [
                        emp.code,
                        emp.name,
                        get_bank_display(cmp_bank) + '/' +get_bank_display(bank),
                        cmp_account_no + '/' +account_no,
                    ]
                    data.append(l)
        else:
            template_name = 'hr/khosomat.html'

            for (emp,badalat,khosomat,draja_wazifia,alawa_sanawia) in payroll.all_employees_payroll_from_db():
                emp_lst.append(emp)
                cmp_draja_wazifia = cmp_alawa_sanawia = None
                try:
                    cmp_emp,cmp_badalat,cmp_khosomat,cmp_draja_wazifia,cmp_alawa_sanawia,*rest = cmp_index[emp.id] #cmp_payroll.employee_payroll_from_employee(emp)
                    khosomat_list = [round((zp[0][1]-zp[1][1]),2) for zp in zip(khosomat,cmp_khosomat)]
                except KeyError:
                    khosomat_list = [round(zp[1],2) for zp in khosomat]
                
                if abs(sum(khosomat_list)) > 0:
                    l = [
                        emp.code,
                        emp.name,
                        cmp_drjat(draja_wazifia,cmp_draja_wazifia),
                        cmp_alawa(alawa_sanawia,cmp_alawa_sanawia),
                    ] + khosomat_list

                    data.append(l)

                    for idx,s in enumerate(khosomat_list):
                        try:
                            summary_list[idx] += khosomat_list[idx]
                        except IndexError:
                            summary_list.insert(idx,khosomat_list[idx])

            #employees not exists in first sheet
            for payroll_detail in PayrollDetail.objects.filter(payroll_master=cmp_payroll.payroll_master).exclude(employee__in=emp_lst).prefetch_related("employee"):
                try:
                    cmp_emp,cmp_badalat,cmp_khosomat,cmp_draja_wazifia,cmp_alawa_sanawia,*rest = cmp_index[payroll_detail.employee.id] #cmp_payroll.employee_payroll_from_employee(payroll_detail.employee)
                    khosomat_list = [round(-zp[1],2) for zp in cmp_khosomat]
                    
                    if abs(sum(khosomat_list)) > 0:
                        l = [
                            cmp_emp.code,
                            cmp_emp.name,
                            cmp_drjat(None,cmp_draja_wazifia),
                            cmp_alawa(None,cmp_alawa_sanawia),
                        ] + khosomat_list
                        data.append(l)

                        for idx,s in enumerate(khosomat_list):
                            try:
                                summary_list[idx] += khosomat_list[idx]
                            except IndexError:
                                summary_list.insert(idx,khosomat_list[idx])
                except: #should review why code may get here.
                    pass

            summary_list = [round(s,2) for s in summary_list]

        if format == 'csv':
            sheet_name = 'net'
            # print(f'attachment; filename="{sheet_name}_{month}_{year}.csv"')
            response = HttpResponse(
                content_type="text/csv",
                headers={"Content-Disposition": f'attachment; filename="{sheet_name}_{month}_{year}.csv"'},
            )

            # BOM
            response.write(codecs.BOM_UTF8)

            writer = csv.writer(response)
            writer.writerow(header)

            if SHOW_CSV_TOTAL:
                data.append(['-','-','-','-',]+summary_list)

            for r in data:
                writer.writerow(r)

            cache.patch_cache_control(response, max_age=0)
            return response

        else:
            context = {
                'title':'كشف فرق استقطاعات',
                'header':header,
                'data': data,
                'summary':summary_list,
                'month':MONTH_CHOICES[month],
                'year':year,
            }

            response = render(self.request,template_name,context)
            cache.patch_cache_control(response, max_age=0)
            return response

class Mobashara(LoginRequiredMixin,UserPermissionMixin,View):
    user_groups = ['hr_manager','hr_payroll']
    def get(self,*args,**kwargs):
        year = self.request.GET['year']
        month = self.request.GET['month']
        format = self.request.GET.get('format',None)
        bank_sheet = self.request.GET.get('bank_sheet',False)
        data = []
        
        mobashara = MobasharaSheet(year,month)

        if bank_sheet:
            template_name = 'hr/bank.html'
            header = ['الرمز','الموظف','البنك','رقم الحساب','صافي الاستحقاق']
            emp_accounts = get_employee_accounts()

            for emp_mobashara in mobashara.all_employees_mobashara_from_db().prefetch_related("employee__mosama_wazifi"):
                emp = emp_mobashara.employee
                try:
                    bnk_no,bank = emp_accounts[emp.id] #employeeemp.employeebankaccount_set.get(active=True).account_no
                except KeyError:
                    bnk_no,bank = ('-','-')

                total = (emp_mobashara.amount+emp_mobashara.amount_m2moria+emp_mobashara.amount_e3asha)
                l = [emp.code,emp.name,bank,bnk_no,round(total,2)]
                data.append(l)
        else:
            template_name = 'hr/mobashara.html'
            header = ['الرمز','الموظف','الدرجة الوظيفية','العلاوة','المسمى الوظيفي','الاستحقاق اليومي','ايام الشهر','ايام المباشرة','ايام الاجازة','ايام التكليف','طوارئ','مأمورية','إعاشة','صافي الاستحقاق']

            summary_list = []

            for emp_mobashara in mobashara.all_employees_mobashara_from_db().prefetch_related("employee__mosama_wazifi"):
                emp = emp_mobashara.employee
                total = (emp_mobashara.amount+emp_mobashara.amount_m2moria+emp_mobashara.amount_e3asha)
                l = [emp.code,emp.name,emp.get_draja_wazifia_display(),emp.get_alawa_sanawia_display(),emp.mosama_wazifi.name,emp_mobashara.rate,emp_mobashara.no_days_month,emp_mobashara.no_days_mobashara,emp_mobashara.no_days_2jazaa,emp_mobashara.no_days_taklif,emp_mobashara.amount,emp_mobashara.amount_m2moria,emp_mobashara.amount_e3asha,total]
                data.append(l)

        if format == 'csv':
            sheet_name = 'mobashara'
            # print(f'attachment; filename="{sheet_name}_{month}_{year}.csv"')
            response = HttpResponse(
                content_type="text/csv",
                headers={"Content-Disposition": f'attachment; filename="{sheet_name}_{month}_{year}.csv"'},
            )

            # BOM
            response.write(codecs.BOM_UTF8)

            writer = csv.writer(response)
            writer.writerow(header)

            for r in data:
                writer.writerow(r)

            cache.patch_cache_control(response, max_age=0)
            return response

        else:
            context = {
                'title':'كشف المباشرة',
                'header':header,
                'data': data,
            }

            response = render(self.request,template_name,context)
            cache.patch_cache_control(response, max_age=0)
            return response

class Mokaf2(LoginRequiredMixin,UserPermissionMixin,View):
    user_groups = ['hr_manager','hr_payroll']
    def get(self,*args,**kwargs):
        year = self.request.GET['year']
        month = self.request.GET['month']
        format = self.request.GET.get('format',None)
        bank_sheet = self.request.GET.get('bank_sheet',False)
        data = []

        try:
            payroll_master = PayrollMaster.objects.get(year=year,month=month)
        except PayrollMaster.DoesNotExist as e:
            bad_request(self.request,e)

        mokaf2 = Mokaf2Sheet(year,month)

        if bank_sheet:
            template_name = 'hr/bank.html'
            header = ['الرمز','الموظف','البنك','رقم الحساب','صافي الاستحقاق']
            emp_accounts = get_employee_accounts()

            for emp_mokaf2 in mokaf2.all_employees_mokaf2_from_db():
                emp = emp_mokaf2.employee
                try:
                    bnk_no,bank = emp_accounts[emp.id] #employeeemp.employeebankaccount_set.get(active=True).account_no
                except KeyError:
                    bnk_no,bank = ('-','-')

                l = [emp.code,emp.name,bank,bnk_no,round(emp_mokaf2.safi_2l2sti7gag,2)]
                data.append(l)
        else:
            template_name = 'hr/mokaf2.html'
            header = ['الرمز','الموظف','الدرجة الوظيفية','العلاوة','اجمالي المرتب','الضريبة','الدمغة',]

            if not payroll_master.khasm_salafiat_elsandog_min_elomoratab:
                header += ['سلفيات الصندوق',]

            header += ['صافي الاستحقاق',]

            summary_list = []

            for (emp,emp_mokaf2) in mokaf2.all_employees_mokaf2_from_db():
                mokaf2_list = [round(k[1],2) for k in emp_mokaf2]
                l = [emp.code,emp.name,emp.get_draja_wazifia_display(),emp.get_alawa_sanawia_display(),]+mokaf2_list #round(emp_mokaf2.ajmali_2lmoratab,2),round(emp_mokaf2.dariba,2),emp_mokaf2.damga,]
                #if not payroll_master.khasm_salafiat_elsandog_min_elomoratab:
                #    l += [round(emp_mokaf2.salafiat_sandog,2),]
                #l +=[round(emp_mokaf2.safi_2l2sti7gag,2),]

                data.append(l)

                for idx,s in enumerate(mokaf2_list):
                    try:
                        summary_list[idx] += mokaf2_list[idx]
                    except IndexError:
                        summary_list.insert(idx,mokaf2_list[idx])

            summary_list = [round(s,2) for s in summary_list]


        if format == 'csv':
            sheet_name = 'bonace'
            # print(f'attachment; filename="{sheet_name}_{month}_{year}.csv"')
            response = HttpResponse(
                content_type="text/csv",
                headers={"Content-Disposition": f'attachment; filename="{sheet_name}_{month}_{year}.csv"'},
            )

            # BOM
            response.write(codecs.BOM_UTF8)

            writer = csv.writer(response)
            writer.writerow(header)

            if SHOW_CSV_TOTAL:
                data.append(['-','-','-','-',]+summary_list)

            for r in data:
                writer.writerow(r)

            cache.patch_cache_control(response, max_age=0)
            return response

        else:
            context = {
                'title':'كشف المكافأة',
                'header':header,
                'data': data,
                'summary':summary_list,
            }

            response = render(self.request,template_name,context)
            cache.patch_cache_control(response, max_age=0)
            return response

class M2moria(LoginRequiredMixin,UserPermissionMixin,View):
    user_groups = ['hr_manager','hr_payroll']
    def get(self,*args,**kwargs):
        year = self.request.GET['year']
        month = self.request.GET['month']
        format = self.request.GET.get('format',None)
        bank_sheet = self.request.GET.get('bank_sheet',False)
        data = []
        
        m2moria = M2moriaSheet(year,month)

        if bank_sheet:
            template_name = 'hr/bank.html'
            header = ['الرمز','الموظف','البنك','رقم الحساب','صافي الاستحقاق']
            emp_accounts = get_employee_accounts()

            for emp_m2moria in m2moria.all_employees_m2moria_from_db():
                emp = emp_m2moria.employee
                try:
                    bnk_no,bank = emp_accounts[emp.id] #employeeemp.employeebankaccount_set.get(active=True).account_no
                except KeyError:
                    bnk_no,bank = ('-','-')

                l = [emp.code,emp.name,bank,bnk_no,round(emp_m2moria.safi_2l2sti7gag,2)]
                data.append(l)
        else:
            template_name = 'hr/mokaf2.html'

            header = ['الرمز','الموظف','الدرجة الوظيفية','العلاوة','اجمالي المرتب','اجر اليوم','عدد الايام','الدمغة','صافي الاستحقاق']

            summary_list = []

            for emp_m2moria in m2moria.all_employees_m2moria_from_db():
                emp = emp_m2moria.employee
                l = [emp.code,emp.name,emp.get_draja_wazifia_display(),emp.get_alawa_sanawia_display(),emp_m2moria.ajmali_2lmoratab,emp_m2moria.ajmali_2lmoratab/30*1.5,emp_m2moria.no_days,emp_m2moria.damga,emp_m2moria.safi_2l2sti7gag]
                data.append(l)

        if format == 'csv':
            sheet_name = 'm2moria'
            # print(f'attachment; filename="{sheet_name}_{month}_{year}.csv"')
            response = HttpResponse(
                content_type="text/csv",
                headers={"Content-Disposition": f'attachment; filename="{sheet_name}_{month}_{year}.csv"'},
            )

            # BOM
            response.write(codecs.BOM_UTF8)

            writer = csv.writer(response)
            writer.writerow(header)

            for r in data:
                writer.writerow(r)

            cache.patch_cache_control(response, max_age=0)
            return response

        else:
            context = {
                'title':'كشف المأمورية',
                'header':header,
                'data': data,
            }

            response = render(self.request,template_name,context)
            cache.patch_cache_control(response, max_age=0)
            return response
