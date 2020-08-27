#-*- coding:utf-8 -*-

from odoo import api, fields, models, _
from itertools import groupby
from odoo.exceptions import ValidationError
from datetime import datetime


class HrPayrollDISA(models.Model):
    _name= 'hr.payroll.disa'
    _description= "Gestion de la DISA"

    date_from = fields.Date("Date de début", required=True)
    date_to = fields.Date("Date de fin", required=True)
    company_id = fields.Many2one('res.company', 'Société', default=1, required=True)
    seq_disa = fields.Char('Sequence', readonly=True)
    total_general_brut = fields.Integer('Total brut annuel', compute='_compute', store=True)
    total_general_cotisation = fields.Integer('Total cotisation', compute='_compute', store=True)
    total_general_retraite = fields.Integer('Total retraite', compute='_compute', store=True)
    total_general_employee = fields.Integer(compute='_compute', store=True)
    total_cotisation_pf_am = fields.Integer(compute='_compute', store=True)
    total_accident = fields.Integer(compute='_compute', store=True)
    # total_retraite = fields.Integer(compute='_compute', store=True)

    @api.model
    def create(self, vals):

        vals['seq_disa'] = self.env['ir.sequence'].next_by_code('hr.payroll.disa')
        return super(HrPayrollDISA, self).create(vals)

    def get_number_worked_hour(self, slips):
        result = []
        number = 0.0
        for slip in slips :
            tmp= slip.worked_days_line_ids.filtered(lambda r: r.code == 'WORK100' or r.code == 'CONG')
            if tmp :
                result+= tmp
        if result:
            number = sum([line.number_of_days for line in result])
        return number

    def get_amount_by_code(self, slips, code, type=None):
        result = []
        amount = 0
        for slip in slips:
            tmp = slip.line_ids.filtered(lambda r: r.code == code)
            if tmp:
                result += tmp
        if result:
            if type is None :
                amount = sum([line.total for line in result])
            else:
                amount = sum([line.amount for line in result])
        return amount
    @api.multi
    def _compute(self):
        slip_obj = self.env['hr.payslip']
        slips = slip_obj.search([('date_from', '>=', self.date_from), ('date_to', '<=', self.date_to)])
        emp_id_double = slips.mapped(lambda r: r.employee_id.id)
        emp_ids = list(set(emp_id_double))
        data = {}
        if slips:
            order = 0
            total_brut = 0
            total_cotisation_pf_am = 0
            total_accident = 0
            total_retraite = 0
            total_emplyee = 0
            for employee, list_slip in groupby(slips, lambda l: l.employee_id):
                order += 1
                e = employee.id
                tmp = list(list_slip)
                val = {
                    'order_num': order,
                    'employee_id': e,
                    'name': employee.name,
                    'cnps': employee.matricule_cnps,
                    'year': employee.birthday[:4],
                    'brut': self.get_amount_by_code(tmp, 'BRUT'),
                    'retraite': self.get_amount_by_code(tmp, 'CNPS', type='pfd'),
                    'cotisation': self.get_amount_by_code(tmp, 'PF', type='pfd'),
                    'accident': self.get_amount_by_code(tmp, 'ACT', type='pfd'),
                    'start_date': employee.start_date,
                    'end_date': employee.end_date,
                    'type': str(employee.type).upper(),
                    'number_hour': self.get_number_worked_hour(tmp),
                    'code_cotisation_employer':'',
                    'disa_id': self.id,
                }
                data[e] = val
                #Tcalcul des totaux ici
                total_brut += int(val['brut'])
                total_cotisation_pf_am += int(val['cotisation'])
                total_accident += int(val['accident'])
                total_retraite += int(val['retraite'])
                total_emplyee += val['order_num']
            self.total_general_brut = round(total_brut)
            self.total_general_cotisation = round(total_cotisation_pf_am) + round(total_accident)
            self.total_general_retraite = round(total_retraite)
            self.total_general_employee = len(emp_ids)
            self.total_accident = round(total_accident)
            self.total_cotisation_pf_am = round(total_cotisation_pf_am)
        return data

    @api.multi
    def _create_lines(self, res):
        disa_line_obj = self.env['hr.disa.line']
        if res:
            for e in res.keys():
                disa_line_obj.search([('employee_id', '=', e)]).unlink()
            for e in res.keys():
                self.env['hr.disa.line'].create(res[e])

    def _print_report(self, data):
        print(data)
        records = self.env[data['model']].browse(data.get('ids', []))
        return self.env.ref('hr_payroll_ci_raport.hr_disa_report').with_context(landscape=True).report_action(self, data=data)

    def getDataByPage(self, data, page_one, page):
        res = {}
        count = 1
        res[count] = data[:page_one]
        index = page_one
        while len(data) > index:
            count += 1
            first = index
            last = index + page
            res[count] = data[first:last]
            index = last
        return res

    @api.multi
    def check_report(self):
        self.ensure_one()
        print(self.id)
        data = {}
        data['ids'] = self.id
        data['model'] = 'hr.payroll.disa'
        data['form'] = self.read(['date_from', 'date_to', 'company_id'])[0]
        d1 = datetime.strptime(data['form']['date_from'], '%Y-%m-%d')
        d2 = datetime.strptime(data['form']['date_to'], '%Y-%m-%d')
        if d1.month != 1 or d2.month != 12:
            raise ValidationError(_("Veuillez entrer une date d'exercice"))
        data['lines'] = self._compute()
        self._create_lines(data['lines'])
        return self._print_report(data)


class hr_disa_line(models.TransientModel):
    _name = 'hr.disa.line'
    _description = "Lignes de la DISA"

    order_num = fields.Integer('NUMERO D’ORDRE', default=0)
    employee_id = fields.Many2one('hr.employee', 'Employé', required=False)
    name = fields.Char('Nom et Prénoms', related="employee_id.name")
    cnps = fields.Char('N° C.N.P.S')
    year = fields.Char('Année \nde naissance')
    start_date = fields.Date("Date \nd'embauche", related="employee_id.start_date")
    end_date = fields.Date('Date \nde depart', related="employee_id.end_date")
    type = fields.Char("Type \nd'employé")
    number_hour = fields.Integer("Nombre \nd'heure de travail", required=False)
    cotisation = fields.Integer("Cotisation", required=False)
    retraite = fields.Integer("Retraite", required=False)
    accident = fields.Integer("Accident", required=False)
    brut = fields.Integer('Brut annuel', required=False)
    code_cotisation_employer = fields.Char('Code cotisation employeur', required=False)
    prestation_familiale = fields.Integer(default=1)
    accident_travail = fields.Integer(default=2)
    assurance_vieilliesse = fields.Integer(default=3)
    assurance_maladie = fields.Integer(default=4)
    disa_id = fields.Many2one('hr.payroll.disa', 'DISA')