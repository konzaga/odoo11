#-*- coding:utf-8 -*-
__author__ = 'lekaizen'


from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from itertools import groupby


months = [(0, 'Janvier'),(1, 'Février'),(2, 'Mars'),(3, 'Avril'),(4, 'Mai'), (5, 'Juin'), (6, 'Juillet'),(7, 'Aout'),
          (8, 'Septembre'),(9, 'Octobre'),(10, 'Novembre'),(11, 'Décembre')]


class HrPayrollFDFP(models.TransientModel):
    _name = 'hr.payroll.fdfp'
    _description = "Gestion des declarations FDFP"

    # name = fields.Char('Nom', required=True, size=155)
    date_from = fields.Date('Debut mois', required=True)
    date_to = fields.Date('Fin mois', required=True)
    company_id= fields.Many2one('res.company', 'Société', default=1)

    def compute_effectif_by_categ(self):
        '''Calcul d'effectif par catégorie :
        Code des catégorie --- E-->Employe, O-->Ouvrier, I-->Cadre, A-->Maitrise'''
        data = {}
        total_employe = 0
        total_ouvrie = 0
        total_cadre = 0
        total_maitrise = 0
        employee_ids = self.env['hr.employee'].search([])
        if employee_ids:
            for c in employee_ids:
                if c.category_id.code == 'E':
                    total_employe +=1
                data['effectif_employes'] = total_employe
                if c.category_id.code == 'O':
                    total_ouvrie +=1
                data['effectif_ouvriers'] = total_ouvrie
                if c.category_id.code == 'I':
                    total_cadre +=1
                data['effectif_cadres'] = total_cadre
                if c.category_id.code == 'A':
                    total_maitrise +=1
                data['effectif_maitrise'] = total_maitrise
            data['total'] = data['effectif_employes'] + data['effectif_ouvriers'] \
                            + data['effectif_cadres'] + data['effectif_maitrise']
            print('test', data)
        return data

    def compute_data(self, date_from, date_to):
        data = {
            'open_emp':   0,
            'open_work':  0,
            'open_cad':   0,
            'open_mait':  0,
            'close_emp':  0,
            'close_work': 0,
            'close_cad':  0,
            'close_mait': 0,
            'total_open': 0,
            'total_close':0
        }
        total_open_emp =   0
        total_open_work =  0
        total_open_cad =   0
        total_open_mait =  0
        total_close_emp =  0
        total_close_work = 0
        total_close_cad =  0
        total_close_mait = 0
        cr = self.env.cr
        cr.execute("SELECT id FROM hr_contract as c WHERE c.date_start BETWEEN %s AND %s AND c.date_end BETWEEN %s AND %s"
                    " OR c.date_start BETWEEN %s AND %s OR c.date_end BETWEEN %s AND %s",\
                   (date_from, date_to,date_from, date_to,date_from, date_to,date_from, date_to))
        contract = [x[0] for x in cr.fetchall()]
        contract_ids = self.env['hr.contract'].browse(contract)
        print(contract_ids)
        if contract_ids:
            for c in contract_ids:
                print(c.state)
                if c.employee_id.category_id.code == 'E' and c.state == 'open':
                    total_open_emp += 1
                data['open_emp'] = total_open_emp
                if c.employee_id.category_id.code == 'O' and c.state == 'open':
                    total_open_work += 1
                data['open_work'] = total_open_work

                if c.employee_id.category_id.code == 'I' and c.state == 'open':
                    total_open_cad += 1
                data['open_cad'] = total_open_cad
                if c.employee_id.category_id.code == 'A' and c.state == 'open':
                    total_open_mait += 1
                data['open_mait'] = total_open_mait
                if c.employee_id.category_id.code == 'E' and c.state == 'close':
                    total_close_emp += 1
                data['close_emp'] = total_close_emp
                if c.employee_id.category_id.code == 'O' and c.state == 'close':
                    total_close_work += 1
                data['close_work'] = total_close_work
                if c.employee_id.category_id.code == 'I' and c.state == 'close':
                    total_close_cad += 1
                data['close_cad'] = total_close_cad
                if c.employee_id.category_id.code == 'A' and c.state == 'close':
                    total_close_mait += 1
                data['close_mait'] = total_close_mait

            data['total_open'] = data['open_emp'] + data['open_work'] \
                                 + data['open_cad'] + data['open_mait']
            data['total_close'] = data['close_emp'] + data['close_work'] \
                                  + data['close_cad'] + data['close_mait']
        return data

    def compute_mensuel(self, date_from, date_to):
        '''BALANCE MENSUELLE DE L'EFFECTIF'''
        data_men = self.compute_data(date_from, date_to)
        print('mensuel',data_men)
        return data_men

    def compute_annuelle(self,date_from, date_to):
        '''BALANCE ANNUELLE DE L'EFFECTIF'''
        date_from = datetime.strptime(date_from, '%Y-%m-%d')
        data = {
            'open_emp': 0,
            'open_work': 0,
            'open_cad': 0,
            'open_mait': 0,
            'close_emp': 0,
            'close_work': 0,
            'close_cad': 0,
            'close_mait': 0,
            'total_open': 0,
            'total_close': 0
        }
        total_open_emp = 0
        total_open_work = 0
        total_open_cad = 0
        total_open_mait = 0
        total_close_emp = 0
        total_close_work = 0
        total_close_cad = 0
        total_close_mait = 0
        if date_from.month == 12:
            begin = date_from + relativedelta(months=-11)
            cr = self.env.cr
            cr.execute("SELECT id FROM hr_contract as c WHERE c.date_start BETWEEN %s AND %s AND c.date_end BETWEEN %s AND %s"
                " OR c.date_start BETWEEN %s AND %s OR c.date_end BETWEEN %s AND %s", \
                (begin, date_to, begin, date_to, begin, date_to, begin, date_to))
            contract = [x[0] for x in cr.fetchall()]
            contract_ids = self.env['hr.contract'].browse(contract)
            if contract_ids:
                for c in contract_ids:
                    print(c.state)
                    if c.employee_id.category_id.code == 'E' and c.state == 'open':
                        total_open_emp += 1
                    data['open_emp'] = total_open_emp
                    if c.employee_id.category_id.code == 'O' and c.state == 'open':
                        total_open_work += 1
                    data['open_work'] = total_open_work

                    if c.employee_id.category_id.code == 'I' and c.state == 'open':
                        total_open_cad += 1
                    data['open_cad'] = total_open_cad
                    if c.employee_id.category_id.code == 'A' and c.state == 'open':
                        total_open_mait += 1
                    data['open_mait'] = total_open_mait
                    if c.employee_id.category_id.code == 'E' and c.state == 'close':
                        total_close_emp += 1
                    data['close_emp'] = total_close_emp
                    if c.employee_id.category_id.code == 'O' and c.state == 'close':
                        total_close_work += 1
                    data['close_work'] = total_close_work
                    if c.employee_id.category_id.code == 'I' and c.state == 'close':
                        total_close_cad += 1
                    data['close_cad'] = total_close_cad
                    if c.employee_id.category_id.code == 'A' and c.state == 'close':
                        total_close_mait += 1
                    data['close_mait'] = total_close_mait

                data['total_open'] = data['open_emp'] + data['open_work'] \
                                     + data['open_cad'] + data['open_mait']
                data['total_close'] = data['close_emp'] + data['close_work'] \
                                      + data['close_cad'] + data['close_mait']
        return data

    def getAmountByCode(self, code, date_from, date_to):
        total = 0
        if code:
            payslip_obj = self.env['hr.payslip']
            slip_ids = payslip_obj.search([('date_from', '>=', date_from), ('date_to', '<=', date_to)])
            if slip_ids :
                for slip in slip_ids:
                    lines = slip.line_ids
                    for l in lines:
                        if l.code == code:
                            total += l.total
            return round(total)

    def versement(self,date_from , date_to):

        masse_salariale = self.getAmountByCode('BRUT', date_from, date_to)
        TAXEFP = self.getAmountByCode('TAXEFP', date_from, date_to)
        versement = abs((masse_salariale * 1.2)/100 - TAXEFP)
        return round(versement)


    def montant_a_payer(self,versement, TAXEFP):
        if self.company_id:
            taux = self.company_id.taux_fdfp_fc
            montant_a_payer = round(versement + (TAXEFP * taux) / 100)
            return montant_a_payer

    def taxe_formation_continue(self, TAXEFP):
        if self.company_id:
            taux = self.company_id.taux_fdfp_fc
            taxe_formation_continue = round((TAXEFP * taux) / 100)
            return taxe_formation_continue

    def taxe_apprentissage(self, TAXEAP):
        if self.company_id:
            taux = self.company_id.taux_fdfp
            taxe_apprentissage = round((TAXEAP * taux) / 100)
            return taxe_apprentissage


    def montant_annuel(self, date_from , date_to):

        masse_salariale = self.getAmountByCode('BRUT', date_from, date_to)
        montant_annuel = round((masse_salariale * 1.2)/100)
        return montant_annuel

    def _print_report(self, data):

        data['form'].update(self.read(['name', 'date_from', 'date_to', 'service_assiette', 'company_id'])[0])
        return self.env.ref('hr_payroll_ci_raport.hr_fdfp_report').with_context(portrait=False).report_action(self, data=data, config=False)

    @api.multi
    def check_report(self, data):
        ''' Button pour l'impression'''
        data['ids'] = self.id
        data['form'] = self.read(['name', 'company_id', 'date_from', 'date_to', 'service_assiette'])[0]
        data['model'] = 'hr.payroll.fdfp'
        data['number'] = self.compute_effectif_by_categ()
        data['annuel'] = self.compute_annuelle(data['form']['date_from'], data['form']['date_to'])
        data['mensuel'] = self.compute_mensuel(data['form']['date_from'], data['form']['date_to'])
        data['TAXEAP'] = self.getAmountByCode('TAXEAP', data['form']['date_from'], data['form']['date_to'])
        data['TAXEFP'] = self.getAmountByCode('TAXEFP', data['form']['date_from'], data['form']['date_to'])
        data['masse_salariale'] = self.getAmountByCode('BRUT', data['form']['date_from'], data['form']['date_to'])
        data['versement'] = self.versement(data['form']['date_from'], data['form']['date_to'])
        data['montant_annuel'] = self.montant_annuel(data['form']['date_from'], data['form']['date_to'])
        data['montant_a_payer'] = self.montant_a_payer(data['versement'], data['TAXEFP'])
        data['taxe_formation_continue'] = self.taxe_formation_continue(data['TAXEFP'])
        data['taxe_apprentissage'] = self.taxe_apprentissage(data['TAXEAP'])

        return self._print_report(data)