import xmlrpc.client
from django.utils.translation import gettext_lazy as _
from .models import OdooConfig

class OdooSync:
    def __init__(self):
        self.config = OdooConfig.get_config()
        if not self.config:
            raise Exception(_("Odoo configuration not found or inactive."))
        
        self.url = self.config.url
        self.db = self.config.db
        self.username = self.config.username
        self.password = self.config.password
        self.uid = None
        self._authenticate()

    def _authenticate(self):
        try:
            common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
            self.uid = common.authenticate(self.db, self.username, self.password, {})
            if not self.uid:
                raise Exception(_("Odoo authentication failed: Invalid credentials or database name."))
        except Exception as e:
            raise Exception(_("Odoo connection error to %s: %s") % (self.url, str(e)))

    def _get_models(self):
        return xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')

    def get_external_id(self, model_name, res_id):
        """Returns the Odoo internal ID for a given external ID (XML ID)"""
        try:
            models = self._get_models()
            name_key = f"{model_name.replace('.', '_')}_{res_id}"
            
            data_ids = models.execute_kw(self.db, self.uid, self.password, 'ir.model.data', 'search', [[
                ('module', '=', 'pa_sync'),
                ('name', '=', name_key)
            ]])
            
            if data_ids:
                res = models.execute_kw(self.db, self.uid, self.password, 'ir.model.data', 'read', [data_ids, ['res_id']])
                return res[0]['res_id']
        except Exception:
            pass
        return None

    def create_with_external_id(self, model_name, res_id, values):
        """Creates or updates a record in Odoo using an external ID for tracking"""
        models = self._get_models()
        odoo_id = self.get_external_id(model_name, res_id)
        
        try:
            if odoo_id:
                models.execute_kw(self.db, self.uid, self.password, model_name, 'write', [[odoo_id], values])
            else:
                odoo_id = models.execute_kw(self.db, self.uid, self.password, model_name, 'create', [values])
                # Register the external ID
                models.execute_kw(self.db, self.uid, self.password, 'ir.model.data', 'create', [{
                    'module': 'pa_sync',
                    'name': f"{model_name.replace('.', '_')}_{res_id}",
                    'model': model_name,
                    'res_id': odoo_id,
                    'noupdate': False,
                }])
            return odoo_id
        except Exception as e:
            error_msg = str(e)
            if hasattr(e, 'faultString'):
                error_msg = e.faultString
            raise Exception(_("Odoo Error [%s]: %s") % (model_name, error_msg))

    def push_company(self, company):
        data = {
            'name': company.name_ar,
            'name_en': company.name_en or '',
            'code': (company.code or '').strip(),
            'email': company.email or '',
            'manager_name': company.manager_name or '',
            'manager_phone': company.manager_phone or '',
            'company_type': company.company_type,
        }
        
        models = self._get_models()
        odoo_id = self.get_external_id('pa.company.production', company.id)
        if not odoo_id and company.code:
            existing_ids = models.execute_kw(self.db, self.uid, self.password, 'pa.company.production', 'search', [[('code', '=', company.code.strip())]])
            if existing_ids:
                odoo_id = existing_ids[0]
                try:
                    models.execute_kw(self.db, self.uid, self.password, 'ir.model.data', 'create', [{
                        'module': 'pa_sync',
                        'name': f"pa_company_production_{company.id}",
                        'model': 'pa.company.production',
                        'res_id': odoo_id,
                    }])
                except Exception: pass

        return self.create_with_external_id('pa.company.production', company.id, data)

    def push_mineral(self, mineral):
        data = {'name': mineral.name}
        models = self._get_models()
        odoo_id = self.get_external_id('pa.lkp.mineral', mineral.id)
        if not odoo_id:
            existing_ids = models.execute_kw(self.db, self.uid, self.password, 'pa.lkp.mineral', 'search', [[('name', '=', mineral.name)]])
            if existing_ids:
                odoo_id = existing_ids[0]
                try:
                    models.execute_kw(self.db, self.uid, self.password, 'ir.model.data', 'create', [{
                        'module': 'pa_sync',
                        'name': f"pa_lkp_mineral_{mineral.id}",
                        'model': 'pa.lkp.mineral',
                        'res_id': odoo_id,
                    }])
                except Exception: pass
        return self.create_with_external_id('pa.lkp.mineral', mineral.id, data)

    def push_item(self, item):
        data = {
            'name': item.name,
            'company_type': item.company_type,
            'calculation_method': item.calculation_method,
        }
        models = self._get_models()
        odoo_id = self.get_external_id('pa.lkp.item', item.id)
        if not odoo_id:
            existing_ids = models.execute_kw(self.db, self.uid, self.password, 'pa.lkp.item', 'search', [[('name', '=', item.name)]])
            if existing_ids:
                odoo_id = existing_ids[0]
                try:
                    models.execute_kw(self.db, self.uid, self.password, 'ir.model.data', 'create', [{
                        'module': 'pa_sync',
                        'name': f"pa_lkp_item_{item.id}",
                        'model': 'pa.lkp.item',
                        'res_id': odoo_id,
                    }])
                except Exception: pass
        return self.create_with_external_id('pa.lkp.item', item.id, data)

    def push_license(self, license):
        company_odoo_id = self.get_external_id('pa.company.production', license.company.id)
        if not company_odoo_id:
            company_odoo_id = self.push_company(license.company)

        mineral_odoo_id = None
        first_mineral = license.mineral.first()
        if first_mineral:
            mineral_odoo_id = self.get_external_id('pa.lkp.mineral', first_mineral.id)
            if not mineral_odoo_id:
                mineral_odoo_id = self.push_mineral(first_mineral)

        data = {
            'company_id': company_odoo_id,
            'license_no': (license.license_no or '').strip(),
            'location': license.location or '',
            'area': license.area or 0.0,
            'contract_status': 'active' if license.contract_status_id == 1 else 'inactive',
            'contract_date': license.start_date.isoformat() if license.start_date else False,
            'signature_date': license.date.isoformat() if license.date else False,
            'expiry_date': license.end_date.isoformat() if license.end_date else False,
            'mineral_id': mineral_odoo_id,
        }
        
        models = self._get_models()
        odoo_id = self.get_external_id('pa.company.license', license.id)
        if not odoo_id and license.license_no:
            existing_ids = models.execute_kw(self.db, self.uid, self.password, 'pa.company.license', 'search', [[('license_no', '=', license.license_no.strip())]])
            if existing_ids:
                odoo_id = existing_ids[0]
                try:
                    models.execute_kw(self.db, self.uid, self.password, 'ir.model.data', 'create', [{
                        'module': 'pa_sync',
                        'name': f"pa_company_license_{license.id}",
                        'model': 'pa.company.license',
                        'res_id': odoo_id,
                    }])
                except Exception: pass

        return self.create_with_external_id('pa.company.license', license.id, data)

    def push_commitment(self, commitment):
        company_odoo_id = self.get_external_id('pa.company.production', commitment.company.id)
        if not company_odoo_id:
            company_odoo_id = self.push_company(commitment.company)

        license_odoo_id = None
        if commitment.license:
            license_odoo_id = self.get_external_id('pa.company.license', commitment.license.id)
            if not license_odoo_id:
                license_odoo_id = self.push_license(commitment.license)

        # Prepare Lines
        line_ids = []
        for line in commitment.tblcompanycommitmentdetail_set.all():
            item_odoo_id = self.get_external_id('pa.lkp.item', line.item.id)
            if not item_odoo_id:
                item_odoo_id = self.push_item(line.item)
            line_ids.append((0, 0, {
                'item_id': item_odoo_id,
                'amount_factor': float(line.amount_factor),
            }))

        data = {
            'company_id': company_odoo_id,
            'license_id': license_odoo_id,
            'currency': commitment.currency,
            'note': commitment.note or '',
            'state': commitment.state,
            'line_ids': line_ids,
        }
        
        # Odoo One2many logic: if updating, we might want to clear old lines first
        odoo_id = self.get_external_id('pa.commitment', commitment.id)
        if odoo_id:
            data['line_ids'] = [(5, 0, 0)] + line_ids
            
        return self.create_with_external_id('pa.commitment', commitment.id, data)

    def push_request(self, request):
        commitment_odoo_id = self.get_external_id('pa.commitment', request.commitment.id)
        if not commitment_odoo_id:
            commitment_odoo_id = self.push_commitment(request.commitment)

        # Prepare Lines
        line_ids = []
        for line in request.tblcompanyrequestdetail_set.all():
            item_odoo_id = self.get_external_id('pa.lkp.item', line.item.id)
            if not item_odoo_id:
                item_odoo_id = self.push_item(line.item)
            line_ids.append((0, 0, {
                'item_id': item_odoo_id,
                'amount': float(line.amount),
            }))

        data = {
            'commitment_id': commitment_odoo_id,
            'from_dt': request.from_dt.isoformat(),
            'to_dt': request.to_dt.isoformat(),
            'currency': request.currency,
            'payment_state': request.payment_state,
            'state': request.state,
            'note': request.note or '',
            'line_ids': line_ids,
        }
        
        odoo_id = self.get_external_id('pa.request', request.id)
        if odoo_id:
            data['line_ids'] = [(5, 0, 0)] + line_ids

        return self.create_with_external_id('pa.request', request.id, data)

    def push_payment(self, payment):
        request_odoo_id = self.get_external_id('pa.request', payment.request.id)
        if not request_odoo_id:
            request_odoo_id = self.push_request(payment.request)

        # Prepare Lines
        line_ids = []
        for line in payment.tblcompanypaymentdetail_set.all():
            item_odoo_id = self.get_external_id('pa.lkp.item', line.item.id)
            if not item_odoo_id:
                item_odoo_id = self.push_item(line.item)
            line_ids.append((0, 0, {
                'item_id': item_odoo_id,
                'amount': float(line.amount),
            }))

        data = {
            'request_id': request_odoo_id,
            'payment_dt': payment.payment_dt.isoformat(),
            'currency': payment.currency,
            'exchange_rate': float(payment.exchange_rate),
            'state': payment.state,
            'note': payment.note or '',
            'line_ids': line_ids,
        }
        
        odoo_id = self.get_external_id('pa.payment', payment.id)
        if odoo_id:
            data['line_ids'] = [(5, 0, 0)] + line_ids

        return self.create_with_external_id('pa.payment', payment.id, data)
