#-*- coding:utf-8 -*-

from odoo import api, fields, models
from itertools import groupby
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime
import locale


trimestre_1 = {'janvier':['2018-01-01','2018-01-31'],'fevrier':['2018-02-01','2018-02-28'],'mars':['2018-03-01', '2018-03-31']}
trimestre_2 = {'avril':['2018-04-01','2018-04-30'], 'mai':['2018-05-01','2018-05-31'],'juin':['2018-06-01','2018-06-30']}
trimestre_3 = {'juillet':['2018-07-01','2018-07-31'],'aout':['2018-08-01','2018-08-31'],'septembre':['2018-09-01','2018-09-30']}
trimestre_4 = {'octobre':['2018-10-01','2018-10-31'],'novembre':['2018-11-01','2018-11-30'],'decembre':['2018-12-01','2018-12-31']}

class HrCnpsMonthly(models.Model):
    _name = 'hr.cnps.trimestriel'
    _description = "Gestion de la CNPS TRIMESTRIEL"


    date_from = fields.Date('Date de début')
    date_to = fields.Date('Date de fin')
    trimestre = fields.Selection([('trimestre_1', 'Premier Trimestre (Janvier-Février-Mars)'),
                                   ('trimestre_2', 'Deuxième Trimestre (Avril-Mai-Juin)'),
                                  ('trimestre_3', 'Troisième Trimestre (Juillet-Août-Septembre)'),
                                   ('trimestre_4', 'Quatrième Trimestre (Octobre-Novembre-Décembre)')],
                                       'Trimestre', required=True)
    company_id= fields.Many2one('res.company', 'Compagnie', required=True, default=1)
    assurance_maternite = fields.Integer('Assurance Maternité',compute='compute', store=True)
    prestation_familiale = fields.Integer('Prestation Familiale', compute='compute', store=True)
    accident_travail = fields.Integer('Accident Travail', compute='compute', store=True)
    regime_retraite = fields.Integer('Régime Retraite', compute='compute', store=True)
    total_cotisation = fields.Integer('Total Cotisation', compute='compute', store=True)
    total_brut = fields.Integer('Total Brut',compute='compute', store=True)
    total_regime_retraite = fields.Integer('Total Régime Retraite', compute='_get_totaux', store=True)
    total_des_regimes = fields.Integer('Total des Régime', compute='_get_totaux', store=True)
    cumul_salaire_retraite = fields.Integer('Cumul retraite')
    cumul_salaire_prestafami_acctrav = fields.Integer('Cumul prestation famille et accident de travail')
    seq_cnps_trim = fields.Char()
    mois_1 = fields.Char()
    mois_2 = fields.Char()
    mois_3 = fields.Char()

    @api.model
    def create(self, vals):

        vals['seq_cnps_trim'] = self.env['ir.sequence'].next_by_code('hr.cnps.trimestriel')
        return super(HrCnpsMonthly, self).create(vals)

    def get_amount_by_code(self, slips, code):
        result = []
        amount = 0
        for slip in slips :
            tmp= slip.line_ids.filtered(lambda r: r.code==code)
            if tmp :
                result+= tmp
        if result :
            amount = sum([line.total for line in result])
        return amount

    def computeBrut(self, type, brut):
        vals = {}
        if type == 'm':
            if brut > 1657315:
                vals['retraite'] = 1657315
                vals['tranche']= 4
            elif brut >= 70000 and brut <= 1657315 :
                vals['retraite']= brut
                vals['tranche']= 3
            else :
                vals['retraite']= brut
                vals['tranche']= 2
            vals['autre_cotisation'] = 70000
        return vals


    def computeValues(self, employee, list_slip):
        # vals = {}
        brut = self.get_amount_by_code(list_slip, 'BRUT')
        print(brut)
        vals= self.computeBrut(employee.type, brut)

    def compute_data(self, data, tranche):
        vals = {
            'tranche': tranche,
            'nombre': 0,
            'retraite': 0,
            'cotisation': 0
        }
        for item in data:
            if item.get('tranche') == tranche:
                vals['nombre'] += 1
                vals['retraite'] += item.get('retraite')
                vals['cotisation'] += item.get('autre_cotisation')
        return vals

    def get_taux(self, company):
        if company:
            vals= {
                'accident': company.taux_accident_travail,
                'cnps': company.taux_cnps_employee_local+ company.taux_cnps_employer,
                'famille': company.taux_prestation_familiale,
                'maternite': company.taux_assurance_mater
            }
            return vals
        return {}

    def _get_totaux(self, data):
        nombre = retraite = cotisation = 0
        for item in data :
            nombre += item.get('nombre')
            retraite += item.get('retraite')
            cotisation += item.get('cotisation')
        # self.total_regime_retraite = retraite
        # self.total_des_regimes = cotisation
        return {
            'nombre': nombre,
            'retraite': retraite,
            'cotisation': cotisation
        }

    @api.multi
    def compute(self):
        self.ensure_one()
        periode = {}
        res_1 = {}
        res_2 = {}
        res_3 = {}
        periode['ids'] = self.id
        periode['model'] = 'hr.cnps.trimestriel'
        lang_code = self.env.context.get('lang') or 'en_US'
        lang = self.env['res.lang']
        lang_id = lang._lang_get(lang_code)
        date_format = lang_id.date_format
        slip_obj = self.env['hr.payslip']

        if self.trimestre == 'trimestre_1':
            print('Premier Trimestre')
            # Date dédut et fin de Janvier
            date_from_j = trimestre_1['janvier'][0]
            date_to_j = trimestre_1['janvier'][1]
            date_from_janvier = datetime.strptime(date_from_j, DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
            date_to_janvier = datetime.strptime(date_to_j, DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
            slips_janvier = slip_obj.search([('date_from', '>=', date_from_janvier), ('date_to', '<=', date_to_janvier),
                                     ('company_id', '=', self.company_id.id)])
            date = datetime.strptime(date_from_j, '%Y-%m-%d')
            res_1['mois'] = date.strftime("%B").upper()
            self.mois_1 = res_1['mois']
            data_janvier = []
            results_janvier = []
            total_brut_janvier = 0
            if slips_janvier:
                order = 0

                for employee, list_slip in groupby(slips_janvier, lambda l: l.employee_id):
                    tmp = list(list_slip)
                    brut = self.get_amount_by_code(tmp, 'BRUT')
                    total_brut_janvier += brut
                    vals = self.computeBrut(employee.type, brut)
                    data_janvier.append(vals)
                for i in range(5):
                    result = self.compute_data(data_janvier, i)
                    results_janvier.append(result)
            res_1['taux'] = self.get_taux(self.company_id)
            res_1['lines'] = results_janvier
            res_1['totaux'] = self._get_totaux(results_janvier)
            res_1['retraite'] = int(res_1['totaux']['retraite'] * (res_1['taux']['cnps'] / 100))
            res_1['accident'] = int(res_1['totaux']['cotisation'] * (res_1['taux']['accident'] / 100))
            res_1['famille'] = int(res_1['totaux']['cotisation'] * (res_1['taux']['famille'] / 100))
            res_1['maternity'] = int(res_1['totaux']['cotisation'] * (res_1['taux']['maternite'] / 100))
            res_1['total_brut'] = total_brut_janvier
            res_1['total_cotisation'] = int(res_1['maternity'] + res_1['famille'] + res_1['accident'] + res_1['retraite'])
            periode['periode_1'] = res_1

            # Date dédut et fin de Février
            date_from_f = trimestre_1['fevrier'][0]
            date_to_f = trimestre_1['fevrier'][1]
            date_from_fevrier = datetime.strptime(date_from_f, DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
            date_to_fevrier = datetime.strptime(date_to_f, DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
            slips_fevrier = slip_obj.search([('date_from', '>=', date_from_fevrier), ('date_to', '<=', date_to_fevrier),
                                     ('company_id', '=', self.company_id.id)])

            res_2['mois'] = 'FEVRIER'
            self.mois_2 = res_2['mois']
            data_fevrier = []
            results_fevrier = []
            total_brut_fevrier = 0
            if slips_fevrier:
                order = 0

                for employee, list_slip in groupby(slips_fevrier, lambda l: l.employee_id):
                    tmp = list(list_slip)
                    brut = self.get_amount_by_code(tmp, 'BRUT')
                    total_brut_fevrier += brut
                    vals = self.computeBrut(employee.type, brut)
                    data_fevrier.append(vals)
                for i in range(5):
                    result = self.compute_data(data_fevrier, i)
                    results_fevrier.append(result)
            res_2['taux'] = self.get_taux(self.company_id)
            res_2['lines'] = results_fevrier
            res_2['totaux'] = self._get_totaux(results_fevrier)
            res_2['retraite'] = int(res_2['totaux']['retraite'] * (res_2['taux']['cnps'] / 100))
            res_2['accident'] = int(res_2['totaux']['cotisation'] * (res_2['taux']['accident'] / 100))
            res_2['famille'] = int(res_2['totaux']['cotisation'] * (res_2['taux']['famille'] / 100))
            res_2['maternity'] = int(res_2['totaux']['cotisation'] * (res_2['taux']['maternite'] / 100))
            res_2['total_brut'] = total_brut_fevrier
            res_2['total_cotisation'] = int(res_2['maternity'] + res_2['famille'] + res_2['accident'] + res_2['retraite'])
            periode['periode_2'] = res_2

            # Date dédut et fin de Mars
            date_from_m = trimestre_1['mars'][0]
            date_to_m = trimestre_1['mars'][1]
            date_from_mars = datetime.strptime(date_from_m, DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
            date_to_mars = datetime.strptime(date_to_m, DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
            slips_mars= slip_obj.search([('date_from', '>=', date_from_mars), ('date_to', '<=', date_to_mars),
                                    ('company_id', '=', self.company_id.id)])
            date = datetime.strptime(date_from_m, '%Y-%m-%d')
            res_3['mois'] = date.strftime("%B").upper()
            self.mois_3 = res_3['mois']
            data_mars = []
            results_mars = []
            total_brut_mars = 0
            if slips_mars :
                order = 0
                for employee, list_slip in groupby(slips_mars, lambda l: l.employee_id):
                    tmp = list(list_slip)
                    brut = self.get_amount_by_code(tmp, 'BRUT')
                    total_brut_mars += brut
                    vals = self.computeBrut(employee.type, brut)
                    data_mars.append(vals)
                for i in range(5):
                    result= self.compute_data(data_mars, i)
                    results_mars.append(result)
            res_3['taux'] = self.get_taux(self.company_id)
            res_3['lines'] = results_mars
            res_3['totaux'] = self._get_totaux(results_mars)
            res_3['retraite'] = int(res_3['totaux']['retraite'] * (res_3['taux']['cnps']/100))
            res_3['accident'] = int(res_3['totaux']['cotisation'] * (res_3['taux']['accident']/100))
            res_3['famille'] = int(res_3['totaux']['cotisation'] * (res_3['taux']['famille']/100))
            res_3['maternity'] = int(res_3['totaux']['cotisation'] * (res_3['taux']['maternite']/100))
            res_3['total_brut'] = total_brut_mars
            res_3['total_cotisation'] = int(res_3['maternity'] + res_3['famille'] + res_3['accident'] + res_3['retraite'])
            periode['periode_3'] = res_3

            periode['cotisation_p'] = periode['periode_1']['totaux']['cotisation'] + periode['periode_2']['totaux']['cotisation'] + periode['periode_3']['totaux']['cotisation']
            periode['retraite_p'] = periode['periode_1']['totaux']['retraite'] + periode['periode_2']['totaux']['retraite'] + periode['periode_3']['totaux']['retraite']
            self.assurance_maternite = int(periode['periode_1']['maternity'] + periode['periode_2']['maternity'] + periode['periode_3']['maternity'])
            self.prestation_familiale = int(periode['periode_1']['famille'] + periode['periode_2']['famille'] + periode['periode_3']['famille'])
            self.accident_travail = int(periode['periode_1']['accident'] + periode['periode_2']['accident'] + periode['periode_3']['accident'])
            self.regime_retraite = int(periode['periode_1']['retraite'] + periode['periode_2']['retraite'] + periode['periode_3']['retraite'])
            self.total_brut = int(periode['periode_1']['total_brut'] + periode['periode_2']['total_brut'] + periode['periode_3']['total_brut'])
            self.total_cotisation = int(periode['periode_1']['total_cotisation'] + periode['periode_2']['total_cotisation'] + periode['periode_3']['total_cotisation'])
            self.date_from = trimestre_1['janvier'][0]
            self.date_to = trimestre_1['mars'][1]
            self.cumul_salaire_retraite = self.regime_retraite
            self.cumul_salaire_prestafami_acctrav = self.assurance_maternite + self.prestation_familiale + self.accident_travail

        if self.trimestre == 'trimestre_2':
            print('Deuxième Trimestre')
            # Date dédut et fin de Avril
            date_from_a = trimestre_2['avril'][0]
            date_to_a = trimestre_2['avril'][1]
            date_from_avril = datetime.strptime(date_from_a, DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
            date_to_avril = datetime.strptime(date_to_a, DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
            slips_avril = slip_obj.search([('date_from', '>=', date_from_avril), ('date_to', '<=', date_to_avril),
                                     ('company_id', '=', self.company_id.id)])
            date = datetime.strptime(date_from_a, '%Y-%m-%d')
            res_1['mois'] = date.strftime("%B").upper()
            self.mois_1 = res_1['mois']
            data_avril = []
            results_avril = []
            total_brut_avril = 0
            if slips_avril:
                order = 0

                for employee, list_slip in groupby(slips_avril, lambda l: l.employee_id):
                    tmp = list(list_slip)
                    brut = self.get_amount_by_code(tmp, 'BRUT')
                    total_brut_avril += brut
                    vals = self.computeBrut(employee.type, brut)
                    data_avril.append(vals)
                for i in range(5):
                    result = self.compute_data(data_avril, i)
                    results_avril.append(result)
            res_1['taux'] = self.get_taux(self.company_id)
            res_1['lines'] = results_avril
            res_1['totaux'] = self._get_totaux(results_avril)
            res_1['retraite'] = int(res_1['totaux']['retraite'] * (res_1['taux']['cnps'] / 100))
            res_1['accident'] = int(res_1['totaux']['cotisation'] * (res_1['taux']['accident'] / 100))
            res_1['famille'] = int(res_1['totaux']['cotisation'] * (res_1['taux']['famille'] / 100))
            res_1['maternity'] = int(res_1['totaux']['cotisation'] * (res_1['taux']['maternite'] / 100))
            res_1['total_brut'] = total_brut_avril
            res_1['total_cotisation'] = int(res_1['maternity'] + res_1['famille'] + res_1['accident'] + res_1['retraite'])
            periode['periode_1'] = res_1

            # Date dédut et fin de Mai
            date_from_m = trimestre_2['mai'][0]
            date_to_m = trimestre_2['mai'][1]
            date_from_mai = datetime.strptime(date_from_m, DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
            date_to_mai = datetime.strptime(date_to_m, DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
            slips_mai = slip_obj.search([('date_from', '>=', date_from_mai), ('date_to', '<=', date_to_mai),
                                     ('company_id', '=', self.company_id.id)])
            date = datetime.strptime(date_from_m, '%Y-%m-%d')
            res_2['mois'] = date.strftime("%B").upper()
            self.mois_2 = res_2['mois']
            data_mai = []
            results_mai = []
            total_brut_mai = 0
            if slips_mai:
                order = 0

                for employee, list_slip in groupby(slips_mai, lambda l: l.employee_id):
                    tmp = list(list_slip)
                    brut = self.get_amount_by_code(tmp, 'BRUT')
                    total_brut_mai += brut
                    vals = self.computeBrut(employee.type, brut)
                    data_mai.append(vals)
                for i in range(5):
                    result = self.compute_data(data_mai, i)
                    results_mai.append(result)
            res_2['taux'] = self.get_taux(self.company_id)
            res_2['lines'] = results_mai
            res_2['totaux'] = self._get_totaux(results_mai)
            res_2['retraite'] = int(res_2['totaux']['retraite'] * (res_2['taux']['cnps'] / 100))
            res_2['accident'] = int(res_2['totaux']['cotisation'] * (res_2['taux']['accident'] / 100))
            res_2['famille'] = int(res_2['totaux']['cotisation'] * (res_2['taux']['famille'] / 100))
            res_2['maternity'] = int(res_2['totaux']['cotisation'] * (res_2['taux']['maternite'] / 100))
            res_2['total_brut'] = total_brut_mai
            res_2['total_cotisation'] = int(res_2['maternity'] + res_2['famille'] + res_2['accident'] + res_2['retraite'])
            periode['periode_2'] = res_2

            # Date dédut et fin de Juin
            date_from_j = trimestre_2['juin'][0]
            date_to_j = trimestre_2['juin'][1]
            date_from_juin = datetime.strptime(date_from_j, DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
            date_to_juin = datetime.strptime(date_to_j, DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
            slips_juin= slip_obj.search([('date_from', '>=', date_from_juin), ('date_to', '<=', date_to_juin),
                                    ('company_id', '=', self.company_id.id)])
            date = datetime.strptime(date_from_j, '%Y-%m-%d')
            res_3['mois'] = date.strftime("%B").upper()
            self.mois_3 = res_3['mois']
            data_juin = []
            results_juin = []
            total_brut_juin = 0
            if slips_juin :
                order = 0
                for employee, list_slip in groupby(slips_juin, lambda l: l.employee_id):
                    tmp = list(list_slip)
                    brut = self.get_amount_by_code(tmp, 'BRUT')
                    total_brut_juin += brut
                    vals = self.computeBrut(employee.type, brut)
                    data_juin.append(vals)
                for i in range(5):
                    result= self.compute_data(data_juin, i)
                    results_juin.append(result)
            res_3['taux'] = self.get_taux(self.company_id)
            res_3['lines'] = results_juin
            res_3['totaux'] = self._get_totaux(results_juin)
            res_3['retraite'] = int(res_3['totaux']['retraite'] * (res_3['taux']['cnps']/100))
            res_3['accident'] = int(res_3['totaux']['cotisation'] * (res_3['taux']['accident']/100))
            res_3['famille'] = int(res_3['totaux']['cotisation'] * (res_3['taux']['famille']/100))
            res_3['maternity'] = int(res_3['totaux']['cotisation'] * (res_3['taux']['maternite']/100))
            res_3['total_brut'] = total_brut_juin
            res_3['total_cotisation'] = int(res_3['maternity'] + res_3['famille'] + res_3['accident'] + res_3['retraite'])
            periode['periode_3'] = res_3

            periode['cotisation_p'] = periode['periode_1']['totaux']['cotisation'] + periode['periode_2']['totaux']['cotisation'] + periode['periode_3']['totaux']['cotisation']
            periode['retraite_p'] = periode['periode_1']['totaux']['retraite'] + periode['periode_2']['totaux']['retraite'] + periode['periode_3']['totaux']['retraite']
            self.assurance_maternite = int(periode['periode_1']['maternity'] + periode['periode_2']['maternity'] + periode['periode_3']['maternity'])
            self.prestation_familiale = int(periode['periode_1']['famille'] + periode['periode_2']['famille'] + periode['periode_3']['famille'])
            self.accident_travail = int(periode['periode_1']['accident'] + periode['periode_2']['accident'] + periode['periode_3']['accident'])
            self.regime_retraite = int(periode['periode_1']['retraite'] + periode['periode_2']['retraite'] + periode['periode_3']['retraite'])
            self.total_brut = int(periode['periode_1']['total_brut'] + periode['periode_2']['total_brut'] + periode['periode_3']['total_brut'])
            self.total_cotisation = int(periode['periode_1']['total_cotisation'] + periode['periode_2']['total_cotisation'] + periode['periode_3']['total_cotisation'])
            self.date_from = trimestre_2['avril'][0]
            self.date_to = trimestre_2['juin'][1]
            self.cumul_salaire_retraite = self.regime_retraite
            self.cumul_salaire_prestafami_acctrav = self.assurance_maternite + self.prestation_familiale + self.accident_travail

        if self.trimestre == 'trimestre_3':
            print('Troisème Trimestre')
            # Date dédut et fin de Juillet
            date_from_ju = trimestre_3['juillet'][0]
            date_to_ju = trimestre_3['juillet'][1]
            date_from_juillet = datetime.strptime(date_from_ju, DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
            date_to_juillet= datetime.strptime(date_to_ju, DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
            slips_juillet = slip_obj.search([('date_from', '>=', date_from_juillet), ('date_to', '<=', date_to_juillet),
                                           ('company_id', '=', self.company_id.id)])
            date = datetime.strptime(date_from_ju, '%Y-%m-%d')
            res_1['mois'] = date.strftime("%B").upper()
            self.mois_1 = res_1['mois']
            data_juillet = []
            results_juillet = []
            total_brut_juillet = 0
            if slips_juillet:
                order = 0

                for employee, list_slip in groupby(slips_juillet, lambda l: l.employee_id):
                    tmp = list(list_slip)
                    brut = self.get_amount_by_code(tmp, 'BRUT')
                    total_brut_juillet += brut
                    vals = self.computeBrut(employee.type, brut)
                    data_juillet.append(vals)
                for i in range(5):
                    result = self.compute_data(data_juillet, i)
                    results_juillet.append(result)
            res_1['taux'] = self.get_taux(self.company_id)
            res_1['lines'] = results_juillet
            res_1['totaux'] = self._get_totaux(results_juillet)
            res_1['retraite'] = int(res_1['totaux']['retraite'] * (res_1['taux']['cnps'] / 100))
            res_1['accident'] = int(res_1['totaux']['cotisation'] * (res_1['taux']['accident'] / 100))
            res_1['famille'] = int(res_1['totaux']['cotisation'] * (res_1['taux']['famille'] / 100))
            res_1['maternity'] = int(res_1['totaux']['cotisation'] * (res_1['taux']['maternite'] / 100))
            res_1['total_brut'] = total_brut_juillet
            res_1['total_cotisation'] = int(res_1['maternity'] + res_1['famille'] + res_1['accident'] + res_1['retraite'])
            periode['periode_1'] = res_1

            # Date dédut et fin de Aout
            date_from_a = trimestre_3['aout'][0]
            date_to_a = trimestre_3['aout'][1]
            date_from_aout = datetime.strptime(date_from_a, DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
            date_to_aout = datetime.strptime(date_to_a, DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
            slips_aout = slip_obj.search([('date_from', '>=', date_from_aout), ('date_to', '<=', date_to_aout),
                                         ('company_id', '=', self.company_id.id)])
            date = datetime.strptime(date_from_a, '%Y-%m-%d')
            res_2['mois'] = date.strftime("%B").upper()
            self.mois_2 = res_2['mois']
            data_aout = []
            results_aout = []
            total_brut_aout = 0
            if slips_aout:
                order = 0

                for employee, list_slip in groupby(slips_aout, lambda l: l.employee_id):
                    tmp = list(list_slip)
                    brut = self.get_amount_by_code(tmp, 'BRUT')
                    total_brut_aout += brut
                    vals = self.computeBrut(employee.type, brut)
                    data_aout.append(vals)
                for i in range(5):
                    result = self.compute_data(data_aout, i)
                    results_aout.append(result)
            res_2['taux'] = self.get_taux(self.company_id)
            res_2['lines'] = results_aout
            res_2['totaux'] = self._get_totaux(results_aout)
            res_2['retraite'] = int(res_2['totaux']['retraite'] * (res_2['taux']['cnps'] / 100))
            res_2['accident'] = int(res_2['totaux']['cotisation'] * (res_2['taux']['accident'] / 100))
            res_2['famille'] = int(res_2['totaux']['cotisation'] * (res_2['taux']['famille'] / 100))
            res_2['maternity'] = int(res_2['totaux']['cotisation'] * (res_2['taux']['maternite'] / 100))
            res_2['total_brut'] = total_brut_aout
            res_2['total_cotisation'] = int(res_2['maternity'] + res_2['famille'] + res_2['accident'] + res_2['retraite'])
            periode['periode_2'] = res_2

            # Date dédut et fin de Septembre
            date_from_s = trimestre_3['septembre'][0]
            date_to_s = trimestre_3['septembre'][1]
            date_from_septembre = datetime.strptime(date_from_s, DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
            date_to_septembre = datetime.strptime(date_to_s, DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
            slips_septembre = slip_obj.search([('date_from', '>=', date_from_septembre), ('date_to', '<=', date_to_septembre),
                                          ('company_id', '=', self.company_id.id)])
            date = datetime.strptime(date_from_s, '%Y-%m-%d')
            res_3['mois'] = date.strftime("%B").upper()
            self.mois_3 = res_3['mois']
            data_septembre = []
            results_septembre = []
            total_brut_septembre = 0
            if slips_septembre:
                order = 0
                for employee, list_slip in groupby(slips_septembre, lambda l: l.employee_id):
                    tmp = list(list_slip)
                    brut = self.get_amount_by_code(tmp, 'BRUT')
                    total_brut_septembre += brut
                    vals = self.computeBrut(employee.type, brut)
                    data_septembre.append(vals)
                for i in range(5):
                    result = self.compute_data(data_septembre, i)
                    results_septembre.append(result)
            res_3['taux'] = self.get_taux(self.company_id)
            res_3['lines'] = results_septembre
            res_3['totaux'] = self._get_totaux(results_septembre)
            res_3['retraite'] = int(res_3['totaux']['retraite'] * (res_3['taux']['cnps'] / 100))
            res_3['accident'] = int(res_3['totaux']['cotisation'] * (res_3['taux']['accident'] / 100))
            res_3['famille'] = int(res_3['totaux']['cotisation'] * (res_3['taux']['famille'] / 100))
            res_3['maternity'] = int(res_3['totaux']['cotisation'] * (res_3['taux']['maternite'] / 100))
            res_3['total_brut'] = total_brut_septembre
            res_3['total_cotisation'] = int(res_3['maternity'] + res_3['famille'] + res_3['accident'] + res_3['retraite'])
            periode['periode_3'] = res_3

            periode['cotisation_p'] = periode['periode_1']['totaux']['cotisation'] + periode['periode_2']['totaux']['cotisation'] + periode['periode_3']['totaux']['cotisation']
            periode['retraite_p'] = periode['periode_1']['totaux']['retraite'] + periode['periode_2']['totaux']['retraite'] + periode['periode_3']['totaux']['retraite']
            self.assurance_maternite = int(periode['periode_1']['maternity'] + periode['periode_2']['maternity'] + periode['periode_3']['maternity'])
            self.prestation_familiale = int(periode['periode_1']['famille'] + periode['periode_2']['famille'] + periode['periode_3']['famille'])
            self.accident_travail = int(periode['periode_1']['accident'] + periode['periode_2']['accident'] + periode['periode_3']['accident'])
            self.regime_retraite = int(periode['periode_1']['retraite'] + periode['periode_2']['retraite'] + periode['periode_3']['retraite'])
            self.total_brut = int(periode['periode_1']['total_brut'] + periode['periode_2']['total_brut'] + periode['periode_3']['total_brut'])
            self.total_cotisation = int(periode['periode_1']['total_cotisation'] + periode['periode_2']['total_cotisation'] + periode['periode_3']['total_cotisation'])
            self.date_from = trimestre_3['juillet'][0]
            self.date_to = trimestre_3['septembre'][1]
            self.cumul_salaire_retraite = self.regime_retraite
            self.cumul_salaire_prestafami_acctrav = self.assurance_maternite + self.prestation_familiale + self.accident_travail

        if self.trimestre == 'trimestre_4':
            print('Quatrième Trimestre')
            # Date dédut et fin de Octobre
            date_from_o = trimestre_4['octobre'][0]
            date_to_o = trimestre_4['octobre'][1]
            date_from_octobre = datetime.strptime(date_from_o, DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
            date_to_octobre= datetime.strptime(date_to_o, DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
            slips_octobre = slip_obj.search([('date_from', '>=', date_from_octobre), ('date_to', '<=', date_to_octobre),
                                           ('company_id', '=', self.company_id.id)])
            date = datetime.strptime(date_from_o, '%Y-%m-%d')
            res_1['mois'] = date.strftime("%B").upper()
            self.mois_1 = res_1['mois']
            data_octobre = []
            results_octobre = []
            total_brut_octobre = 0
            if slips_octobre:
                order = 0

                for employee, list_slip in groupby(slips_octobre, lambda l: l.employee_id):
                    tmp = list(list_slip)
                    brut = self.get_amount_by_code(tmp, 'BRUT')
                    total_brut_octobre += brut
                    vals = self.computeBrut(employee.type, brut)
                    data_octobre.append(vals)
                for i in range(5):
                    result = self.compute_data(data_octobre, i)
                    results_octobre.append(result)
            res_1['taux'] = self.get_taux(self.company_id)
            res_1['lines'] = results_octobre
            res_1['totaux'] = self._get_totaux(results_octobre)
            res_1['retraite'] = int(res_1['totaux']['retraite'] * (res_1['taux']['cnps'] / 100))
            res_1['accident'] = int(res_1['totaux']['cotisation'] * (res_1['taux']['accident'] / 100))
            res_1['famille'] = int(res_1['totaux']['cotisation'] * (res_1['taux']['famille'] / 100))
            res_1['maternity'] = int(res_1['totaux']['cotisation'] * (res_1['taux']['maternite'] / 100))
            res_1['total_brut'] = total_brut_octobre
            res_1['total_cotisation'] = int(res_1['maternity'] + res_1['famille'] + res_1['accident'] + res_1['retraite'])
            periode['periode_1'] = res_1

            # Date dédut et fin de Novembre
            date_from_no = trimestre_4['novembre'][0]
            date_to_no = trimestre_4['novembre'][1]
            date_from_novembre = datetime.strptime(date_from_no, DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
            date_to_novembre = datetime.strptime(date_to_no, DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
            slips_novembre = slip_obj.search([('date_from', '>=', date_from_novembre), ('date_to', '<=', date_to_novembre),
                                         ('company_id', '=', self.company_id.id)])
            date = datetime.strptime(date_from_no, '%Y-%m-%d')
            res_2['mois'] = date.strftime("%B").upper()
            self.mois_2 = res_2['mois']
            data_novembre = []
            results_novembre = []
            total_brut_novembre = 0
            if slips_novembre:
                order = 0

                for employee, list_slip in groupby(slips_novembre, lambda l: l.employee_id):
                    tmp = list(list_slip)
                    brut = self.get_amount_by_code(tmp, 'BRUT')
                    total_brut_novembre += brut
                    vals = self.computeBrut(employee.type, brut)
                    data_novembre.append(vals)
                for i in range(5):
                    result = self.compute_data(data_novembre, i)
                    results_novembre.append(result)
            res_2['taux'] = self.get_taux(self.company_id)
            res_2['lines'] = results_novembre
            res_2['totaux'] = self._get_totaux(results_novembre)
            res_2['retraite'] = int(res_2['totaux']['retraite'] * (res_2['taux']['cnps'] / 100))
            res_2['accident'] = int(res_2['totaux']['cotisation'] * (res_2['taux']['accident'] / 100))
            res_2['famille'] = int(res_2['totaux']['cotisation'] * (res_2['taux']['famille'] / 100))
            res_2['maternity'] = int(res_2['totaux']['cotisation'] * (res_2['taux']['maternite'] / 100))
            res_2['total_brut'] = round(total_brut_novembre)
            res_2['total_cotisation'] = int(res_2['maternity'] + res_2['famille'] + res_2['accident'] + res_2['retraite'])
            periode['periode_2'] = res_2

            # Date dédut et fin de Decembre
            date_from_de = trimestre_4['decembre'][0]
            date_to_de = trimestre_4['decembre'][1]
            date_from_decembre = datetime.strptime(date_from_de, DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
            date_to_decembre = datetime.strptime(date_to_de, DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
            slips_decembre = slip_obj.search([('date_from', '>=', date_from_decembre), ('date_to', '<=', date_to_decembre),
                                          ('company_id', '=', self.company_id.id)])
            date = datetime.strptime(date_from_de, '%Y-%m-%d')
            res_3['mois'] = 'DECEMBRE'
            self.mois_3 = res_3['mois']
            data_decembre = []
            results_decembre = []
            total_brut_decembre = 0
            if slips_decembre:
                order = 0
                for employee, list_slip in groupby(slips_decembre, lambda l: l.employee_id):
                    tmp = list(list_slip)
                    brut = self.get_amount_by_code(tmp, 'BRUT')
                    total_brut_decembre += brut
                    vals = self.computeBrut(employee.type, brut)
                    data_decembre.append(vals)
                for i in range(5):
                    result = self.compute_data(data_decembre, i)
                    results_decembre.append(result)
            res_3['taux'] = self.get_taux(self.company_id)
            res_3['lines'] = results_decembre
            res_3['totaux'] = self._get_totaux(results_decembre)
            res_3['retraite'] = round(int(res_3['totaux']['retraite'] * (res_3['taux']['cnps'] / 100)))
            res_3['accident'] = round(int(res_3['totaux']['cotisation'] * (res_3['taux']['accident'] / 100)))
            res_3['famille'] = round(int(res_3['totaux']['cotisation'] * (res_3['taux']['famille'] / 100)))
            res_3['maternity'] = round(int(res_3['totaux']['cotisation'] * (res_3['taux']['maternite'] / 100)))
            res_3['total_brut'] = round(total_brut_decembre)
            res_3['total_cotisation'] = round(int(res_3['maternity'] + res_3['famille'] + res_3['accident'] + res_3['retraite']))
            periode['periode_3'] = res_3

            periode['cotisation_p'] = periode['periode_1']['totaux']['cotisation'] + periode['periode_2']['totaux']['cotisation'] + periode['periode_3']['totaux']['cotisation']
            periode['retraite_p'] = periode['periode_1']['totaux']['retraite'] + periode['periode_2']['totaux']['retraite'] + periode['periode_3']['totaux']['retraite']
            self.assurance_maternite = round(int(periode['periode_1']['maternity'] + periode['periode_2']['maternity'] + periode['periode_3']['maternity']))
            self.prestation_familiale = round(int(periode['periode_1']['famille'] + periode['periode_2']['famille'] + periode['periode_3']['famille']))
            self.accident_travail = round(int(periode['periode_1']['accident'] + periode['periode_2']['accident'] + periode['periode_3']['accident']))
            self.regime_retraite = round(int(periode['periode_1']['retraite'] + periode['periode_2']['retraite'] + periode['periode_3']['retraite']))
            self.total_brut = round(int(periode['periode_1']['total_brut'] + periode['periode_2']['total_brut'] + periode['periode_3']['total_brut']))
            self.total_cotisation = round(int(periode['periode_1']['total_cotisation'] + periode['periode_2']['total_cotisation'] + periode['periode_3']['total_cotisation']))
            self.date_from = trimestre_4['octobre'][0]
            self.date_to = trimestre_4['decembre'][1]
            self.cumul_salaire_retraite = self.regime_retraite
            self.cumul_salaire_prestafami_acctrav = self.assurance_maternite + self.prestation_familiale + self.accident_travail

        print(periode)
        return self._print_report(periode)

    def _print_report(self, data):
        # model = 'hr.cnps.trimestriel'
        # records = self.env[model].browse(data.get('ids', []))
        records = self.env[data['model']].browse(data.get('ids', []))
        # return self.env['report'].with_context(landscape=True).get_action(records, 'hr_payroll_ci_raport.cnps_trimestriel_report', data=data)
        return self.env.ref('hr_payroll_ci_raport.hr_cnps_trimestriel_report').with_context(landscape=True).report_action(self,
                                                                                                              data=data,
                                                                                                              config=False)