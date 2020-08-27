# -*- encoding: utf-8 -*-

##############################################################################
#
# Copyright (c) 2014 Veone - support.veone.net
# Author: Veone
#
# Fichier du module hr_payroll_ci
# ##############################################################################  -->


import time
from datetime import datetime
from datetime import time as datetime_time
from dateutil import relativedelta

import babel

from odoo import api, fields, models, tools, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from collections import namedtuple

import babel

import odoo.addons.decimal_precision as dp
from odoo.tools import format_amount



class hr_payslip(models.Model):
    _inherit="hr.payslip"
       
    def get_days_periode(self,start, end):
        r = (end + timedelta(days=1) - start).days
        return [start+timedelta(days=i) for i in range(r)]

    @api.multi
    def write(self, vals):
        emp_obj = self.env['hr.employee']
        trouver = False
        for payslip in self:
            employee=payslip.employee_id
            list_payslips=employee.slip_ids
            date_from = datetime.strptime(payslip.date_from,'%Y-%m-%d')
            date_to = datetime.strptime(payslip.date_to,'%Y-%m-%d')
            Range = namedtuple('Range',['start','end'])
            r1=Range(start=date_from,end=date_to)
            new_list=[]
            if (len(list_payslips)!=1):
                for slip in list_payslips:
                    if slip.id != payslip.id :
                        new_list.append(slip)
                for slip in new_list:
                    old_date_from=datetime.strptime(slip.date_from,'%Y-%m-%d')
                    old_date_to = datetime.strptime(slip.date_to,'%Y-%m-%d')
                    r2=Range(start=old_date_from,end=old_date_to)
                    result = (min(r1.end, r2.end)  - max(r1.start,r2.start)).days + 1
                    if result > 0 and slip.contract_id.categorie_id == payslip.contract_id.categorie_id: 
                        trouver = True 
            if trouver == True :
                raise osv.except_osv(_('Warning'),_("L'employé possède déjà un bulletin pour cette période"))                                  
            else :
                super(hr_payslip,self).write(vals)
        return True
         
    def get_test(self,cr, uid,ids,employee_id, context=None):
        res = {}
        obj_payslip = self.pool.get('hr.payslip')
        for emp in self.browse(cr, uid, ids, context=context):
            contract_ids = obj_payslip.search(cr, uid, [('employee_id','=',emp.id),], context=context)
            if contract_ids:
                raise osv.except_osv(_("test"),_("test"))


    @api.onchange('employee_id', 'date_from', 'date_to')
    def onchange_employee(self):

        if (not self.employee_id) or (not self.date_from) or (not self.date_to):
            self.input_line_ids = []
            self.worked_days_line_ids = []
            self.contract_id = False
            self.struct_id = False
            self.name = False
            return

        employee = self.employee_id
        date_from = self.date_from
        date_to = self.date_to
        contract_ids = []

        ttyme = datetime.fromtimestamp(time.mktime(time.strptime(date_from, "%Y-%m-%d")))
        locale = self.env.context.get('lang') or 'en_US'
        self.name = _('Salary Slip of %s for %s') % (employee.name, tools.ustr(babel.dates.format_date(date=ttyme, format='MMMM-y', locale=locale)))
        self.company_id = employee.company_id

        if not self.env.context.get('contract') or not self.contract_id:
            contract_ids = self.get_contract(employee, date_from, date_to)
            if not contract_ids:
                return
            self.contract_id = self.env['hr.contract'].browse(contract_ids[0])

        if not self.contract_id.struct_id:
            return
        self.struct_id = self.contract_id.struct_id

        #computation of the salary input
        contracts = self.env['hr.contract'].browse(contract_ids)
        worked_days_line_ids = self.get_worked_day_lines(contracts, date_from, date_to)
        worked_days_lines = self.worked_days_line_ids.browse([])
        for r in worked_days_line_ids:
            worked_days_lines += worked_days_lines.new(r)
        self.worked_days_line_ids = worked_days_lines

        input_line_ids = self.get_inputs(contracts, date_from, date_to)
        input_lines = self.input_line_ids.browse([])
        for r in input_line_ids:
            input_lines += input_lines.new(r)
        self.input_line_ids = input_lines
        return


    def get_emprunt_montant_monthly(self, employee_id, date_from, date_to):
        ech_obj = self.env['hr.emprunt.loaning.line']
        if employee_id and date_from and date_to:
            lines = ech_obj.search([]).filtered(lambda l: l.loaning_id.employee_id == employee_id and l.statut_echeance == False)
            #print lines
            true_line = lines.filtered(lambda t: t.date_prevu >= date_from and t.date_prevu <= date_to)
            return true_line
        return False

    @api.model
    def _get_payslip_lines(self, contract_ids, payslip_id):
        def _sum_salary_rule_category(localdict, category, amount):
            if category.parent_id:
                localdict = _sum_salary_rule_category(localdict, category.parent_id, amount)
            localdict['categories'].dict[category.code] = category.code in localdict['categories'].dict and localdict['categories'].dict[category.code] + amount or amount
            return localdict

        class BrowsableObject(object):
            def __init__(self, employee_id, dict, env):
                self.employee_id = employee_id
                self.dict = dict
                self.env = env

            def __getattr__(self, attr):
                return attr in self.dict and self.dict.__getitem__(attr) or 0.0

        class InputLine(BrowsableObject):
            """a class that will be used into the python code, mainly for usability purposes"""
            def sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = fields.Date.today()
                self.env.cr.execute("""
                    SELECT sum(amount) as sum
                    FROM hr_payslip as hp, hr_payslip_input as pi
                    WHERE hp.employee_id = %s AND hp.state = 'done'
                    AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s""",
                    (self.employee_id, from_date, to_date, code))
                return self.env.cr.fetchone()[0] or 0.0

        class WorkedDays(BrowsableObject):
            """a class that will be used into the python code, mainly for usability purposes"""
            def _sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = fields.Date.today()
                self.env.cr.execute("""
                    SELECT sum(number_of_days) as number_of_days, sum(number_of_hours) as number_of_hours
                    FROM hr_payslip as hp, hr_payslip_worked_days as pi
                    WHERE hp.employee_id = %s AND hp.state = 'done'
                    AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s""",
                    (self.employee_id, from_date, to_date, code))
                return self.env.cr.fetchone()

            def sum(self, code, from_date, to_date=None):
                res = self._sum(code, from_date, to_date)
                return res and res[0] or 0.0

            def sum_hours(self, code, from_date, to_date=None):
                res = self._sum(code, from_date, to_date)
                return res and res[1] or 0.0

        class Payslips(BrowsableObject):
            """a class that will be used into the python code, mainly for usability purposes"""

            def sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = fields.Date.today()
                self.env.cr.execute("""SELECT sum(case when hp.credit_note = False then (pl.total) else (-pl.total) end)
                            FROM hr_payslip as hp, hr_payslip_line as pl
                            WHERE hp.employee_id = %s AND hp.state = 'done'
                            AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pl.slip_id AND pl.code = %s""",
                            (self.employee_id, from_date, to_date, code))
                res = self.env.cr.fetchone()
                return res and res[0] or 0.0

            def arrondi(self,montant):
                montant = Decimal(str(round(montant,0)))
                return float(montant)

        #we keep a dict with the result because a value can be overwritten by another rule with the same code
        result_dict = {}
        rules_dict = {}
        worked_days_dict = {}
        inputs_dict = {}
        blacklist = []
        payslip = self.env['hr.payslip'].browse(payslip_id)
        for worked_days_line in payslip.worked_days_line_ids:
            worked_days_dict[worked_days_line.code] = worked_days_line
        for input_line in payslip.input_line_ids:
            inputs_dict[input_line.code] = input_line

        categories = BrowsableObject(payslip.employee_id.id, {}, self.env)
        inputs = InputLine(payslip.employee_id.id, inputs_dict, self.env)
        worked_days = WorkedDays(payslip.employee_id.id, worked_days_dict, self.env)
        payslips = Payslips(payslip.employee_id.id, payslip, self.env)
        rules = BrowsableObject(payslip.employee_id.id, rules_dict, self.env)

        baselocaldict = {'categories': categories, 'rules': rules, 'payslip': payslips, 'worked_days': worked_days, 'inputs': inputs}
        #get the ids of the structures on the contracts and their parent id as well
        contracts = self.env['hr.contract'].browse(contract_ids)
        structure_ids = contracts.get_all_structures()
        #get the rules of the structure and thier children
        rule_ids = self.env['hr.payroll.structure'].browse(structure_ids).get_all_rules()
        #run the rules by sequence
        sorted_rule_ids = [id for id, sequence in sorted(rule_ids, key=lambda x:x[1])]
        sorted_rules = self.env['hr.salary.rule'].browse(sorted_rule_ids)

        for contract in contracts:
            employee = contract.employee_id
            localdict = dict(baselocaldict, employee=employee, contract=contract)
            for rule in sorted_rules:
                key = rule.code + '-' + str(contract.id)
                localdict['result'] = None
                localdict['result_qty'] = 1.0
                localdict['result_rate'] = 100
                #check if the rule can be applied
                if rule._satisfy_condition(localdict) and rule.id not in blacklist:
                    #compute the amount of the rule
                    amount, qty, rate = rule._compute_rule(localdict)
                    #check if there is already a rule computed with that code
                    previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
                    #set/overwrite the amount computed for this rule in the localdict
                    tot_rule = amount * qty * rate / 100.0
                    localdict[rule.code] = tot_rule
                    rules_dict[rule.code] = rule
                    #sum the amount for its salary category
                    localdict = _sum_salary_rule_category(localdict, rule.category_id, tot_rule - previous_amount)
                    #create/overwrite the rule in the temporary results
                    result_dict[key] = {
                        'salary_rule_id': rule.id,
                        'contract_id': contract.id,
                        'name': rule.name,
                        'code': rule.code,
                        'category_id': rule.category_id.id,
                        'sequence': rule.sequence,
                        'appears_on_payslip': rule.appears_on_payslip,
                        'condition_select': rule.condition_select,
                        'condition_python': rule.condition_python,
                        'condition_range': rule.condition_range,
                        'condition_range_min': rule.condition_range_min,
                        'condition_range_max': rule.condition_range_max,
                        'amount_select': rule.amount_select,
                        'amount_fix': rule.amount_fix,
                        'amount_python_compute': rule.amount_python_compute,
                        'amount_percentage': rule.amount_percentage,
                        'amount_percentage_base': rule.amount_percentage_base,
                        'register_id': rule.register_id.id,
                        'amount': amount,
                        'employee_id': contract.employee_id.id,
                        'quantity': qty,
                        'rate': rate,
                    }
                else:
                    #blacklist this rule and its children
                    blacklist += [id for id, seq in rule._recursive_search_of_rules()]

        return list(result_dict.values())


    @api.one
    @api.depends('contract_id')
    def _get_anciennete(self):
        anciennete={}
        #print self
        end_date = fields.Datetime.from_string(self.date_to)
        start_date = fields.Datetime.from_string(self.employee_id.start_date)
        tmp = relativedelta.relativedelta(end_date, start_date)
        print(tmp)

        self.payslip_an_anciennete= tmp.years
        self.payslip_mois_anciennete= tmp.months

    @api.onchange('employee_id', 'contract_id')
    def getAnciennete(self):
        for payslip in self :
            print(payslip.date_from)

    @api.one
    def _get_last_payslip(self):
        dic={}
        res=[]
        slips = self.employee_id.slip_ids
        if (len(slips)==1 ) :
            self.last_payslip = False
        else :
            for slip in slips:
                if (slip.id < self.id) :
                    res.append(slip)
                    if len(res)>= 1 :
                        dernier=res[len(res)-1]
                        payslip=self.self.env['hr.payslip'].search([('id','=',dernier.id)])
                        self.last_payslip =  payslip.id

    @api.one
    def _get_total_gain(self):
        res={}
        #line_obj=self.pool.get("hr.payslip.line")
        for line in self.line_ids :
            if line.code=='BRUT':
                self.total_gain = line.total
        return res

    @api.one
    def _get_retenues(self):
        for line in self.line_ids :
            if line.code=='RET':
                self.total_retenues =line.total

    @api.depends('line_ids.total')
    def _get_net_paye(self):
        for slip in self:
            for line in slip.line_ids :
                if line.code=="NET" :
                    slip.update({
                        'net_paie': line.total,
                    })
    
    def get_amountbycode(self, code, line_ids ):
        # line_obj = self.env['hr.payslip.line']
        amount = 0
        if line_ids :
            for line in line_ids :
                if line.code == code :
                    return line.amount
        return 0


    def cumulBYCode(self, employee_id, code, date_from, date_to):
        slip_obj = self.env['hr.payslip']
        payslips= slip_obj.search([('date_from', '>=', date_from), ('date_to', '<=', date_to),
                                     ('employee_id', '=', employee_id)])
        print(payslips)
        total_amount = 0
        for slip in payslips :
            result = slip.get_amountbycode(code, slip.line_ids)
            #print result
            total_amount+= result
        return total_amount


    def get_cumul_base_impot(self):
        year = datetime.now().year
        date_temp = datetime.strptime(self.date_from,'%Y-%m-%d')
        #print date_temp
        first_day= str(date_temp + relativedelta.relativedelta(month=1, day=1))[:10]
        #print first_day
        # print self.date_from
        for payslip in self:
            total = payslip.cumulBYCode(payslip.employee_id.id, 'SNI', first_day, payslip.date_from)
            worked_days = payslip.cumulBYCode(payslip.employee_id.id, 'TJRPAY', first_day, payslip.date_from)
            date_to = fields.Datetime.from_string(payslip.date_to)
            payslip.update({
                'cumul_base_impot': payslip.cumulBYCode(payslip.employee_id.id, 'SNI', first_day, payslip.date_from),
                'cumul_cn': payslip.cumulBYCode(payslip.employee_id.id, 'CN', first_day, payslip.date_from),
                'cumul_worked_days': payslip.cumulBYCode(payslip.employee_id.id, 'TJRPAY', first_day, payslip.date_from),
                'cumul_igr': payslip.cumulBYCode(payslip.employee_id.id, 'IGR', first_day, payslip.date_from),
                'number_of_month': date_to.month
            })

    def get_somme_rubrique(self, code):
        cpt = 0
        annee= fields.Datetime.from_string(self.date_to).year
        print(type(annee))
        lines = self.env['hr.payslip.line'].search([('code', '=', code)]).filtered(lambda p: int(p.slip_id.date_to[0:4]) == annee and
                             p.slip_id.date_to < self.date_to and p.slip_id.employee_id == self.employee_id)

        if lines :
            cpt = sum([l.total for l in lines])
        result = format_amount.manageSeparator(cpt)
        return result

    def get_amount_rubrique(self, rubrique):
        # for id in range(len(obj)):
        line_ids=self.line_ids
        total=0
        for line in line_ids :
            if line.code == rubrique :
                total = line.total
        result = format_amount.manageSeparator(total)
        return result

    def getTauxByCode(self,rubrique):
        # for id in range(len(obj)):
        taux = 0.0
        lines = self.line_ids
        for line in lines:
            if line.code == rubrique:
                #print line.rate
                taux = line.rate
        return taux

    def getLineByCode(self, code):
        # for id in range(len(obj)):
        lines=self.line_ids
        for line in lines:
            if line.code == code:
                return line

    def _get_total(self):
        #print self.get_amount_rubrique('TJRPAY')
        self.worked_days= 0.0

    @api.model
    def get_worked_day_lines(self, contracts, date_from, date_to):
        """
        @param contract: Browse record of contracts
        @return: returns a list of dict containing the input that should be applied for the given contract between date_from and date_to
        """
        res = []
        # fill only if the contract as a working schedule linked
        for contract in contracts.filtered(lambda contract: contract.resource_calendar_id):
            day_from = datetime.combine(fields.Date.from_string(date_from), datetime_time.min)
            day_to = datetime.combine(fields.Date.from_string(date_to), datetime_time.max)

            # compute leave days
            leaves = {}
            day_leave_intervals = contract.employee_id.iter_leaves(day_from, day_to,
                                                                   calendar=contract.resource_calendar_id)
            for day_intervals in day_leave_intervals:
                for interval in day_intervals:
                    holiday = interval[2]['leaves'].holiday_id
                    current_leave_struct = leaves.setdefault(holiday.holiday_status_id, {
                        'name': holiday.holiday_status_id.name,
                        'sequence': 5,
                        'code': holiday.holiday_status_id.name,
                        'number_of_days': 0.0,
                        'number_of_hours': 0.0,
                        'contract_id': contract.id,
                    })
                    leave_time = (interval[1] - interval[0]).seconds / 3600
                    current_leave_struct['number_of_hours'] += leave_time
                    work_hours = contract.employee_id.get_day_work_hours_count(interval[0].date(),
                                                                               calendar=contract.resource_calendar_id)
                    if work_hours:
                        current_leave_struct['number_of_days'] += leave_time / work_hours

            # compute worked days
            work_data = contract.employee_id.get_work_days_data(day_from, day_to,
                                                                calendar=contract.resource_calendar_id)
            attendances = {
                'name': _("Normal Working Days paid at 100%"),
                'sequence': 1,
                'code': 'WORK100',
                'number_of_days': 30,
                'number_of_hours': 173.33,
                'contract_id': contract.id,
            }

            res.append(attendances)
            res.extend(leaves.values())
        return res
    

    option_salaire= fields.Selection([('mois','Mensuel'),('jour','Journalier'),('heure','horaire')],
                         'Option salaire', select=True, readonly=False)
    reference_reglement= fields.Char('Reférence',size=60,required=False)
    payslip_an_anciennete= fields.Integer("Nombre d'année", compute=_get_anciennete)
    payslip_mois_anciennete= fields.Integer("Nombre de mois", compute=_get_anciennete)
    payment_method= fields.Selection([('espece','Espèces'),('virement','Virement bancaire'),('cheque','Chèques')],
                      string='Moyens de paiement',required=False,deafult='espece')
    last_payslip= fields.Many2one("hr.payslip",compute=_get_last_payslip,store=True,string="Dernier bulletin")
    total_gain= fields.Integer(compute=_get_total_gain,store=True)
    total_retenues= fields.Integer(compute=_get_retenues,store=True)
    net_paie= fields.Integer(compute=_get_net_paye,store=True)
    cumul_base_impot = fields.Float('Cumul base impôt', compute=get_cumul_base_impot)
    cumul_cn = fields.Float('Cumul CN payé', compute=get_cumul_base_impot)
    cumul_igr = fields.Float('Cumul IGR payé', compute=get_cumul_base_impot)
    cumul_worked_days= fields.Float('Cumul jours travaillés', compute=get_cumul_base_impot)
    worked_days= fields.Float('Total jours travaillés', compute=_get_total)
    number_of_month= fields.Integer('Nombre de mois', compute='get_cumul_base_impot')


    
    def get_list_employee(self,cr,uid,ids,date_to,context=None): 
        list_employees=[]
        hc_obj=self.pool.get('hr.contract')
        hcontract_ids=hc_obj.search(cr,uid,[('state','=','in_progress')])
        cr.execute("SELECT employee_id FROM hr_contract WHERE id=ANY(%s)", (hcontract_ids,))
        results=cr.fetchall()
        if results :
             list_employees=[res[0] for res in results]
             return {'domain':{'employee_id':[('id','in',list_employees)]}}

    def get_net_paye(self):
        montant = 0
        #line_obj=self.pool.get("hr.payslip.line")
        for line in self.line_ids :
                if line.code=="NET" :
                    montant = line.total
                    #print 'Montant du net %s'%montant
        return montant


class hr_payslip_line(models.Model):
    '''
    Payslip Line
    '''

    _name = 'hr.payslip.line'
    _inherit = 'hr.payslip.line'

    @api.multi
    def _calculate_total(self):
        if not self: return {}
        res = {}
        for line in self:
            self.total = float(line.quantity) * line.amount * line.rate / 100

    amount = fields.Float('Amount', digits=(16, 0))
    quantity = fields.Float('Quantity', digits=(16, 2))
    rate = fields.Float(string='Rate (%)', digits=(16, 2), default=100)
    total = fields.Float(compute='_compute_total', string='Total', digits=(16, 0), store=True)


class hr_salary_rule(models.Model):
    _inherit = 'hr.salary.rule'
    _order = 'sequence'


class HrPayslipWorkedDays(models.Model):
    _inherit = 'hr.payslip.worked_days'

    @api.onchange('number_of_days', 'number_of_hours')
    def onChangeElementWD(self):
        if self.code == 'WORK100':
            self.rate = (self.number_of_days / 30)
            self.number_of_hours = (self.number_of_days * 173.33) / 30

    rate = fields.Float('Taux')


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    @api.one
    def recompute_payslip(self):
        for slip in self.slip_ids :
            slip.compute_sheet()



