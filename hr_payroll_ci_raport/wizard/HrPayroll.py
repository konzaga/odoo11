#-*- coding:utf-8 -*-
__author__ = 'lekaizen'


from odoo import fields, models, api, _
from odoo.exceptions import UserError


class HrPayroll(models.TransientModel):
    _name = 'hr.payroll.payroll'
    _description = "Gestion des livres de paie"

    name = fields.Char('Nom', required=True, size=155)
    # lot_id = fields.Many2one('h.payslip.run', 'Lot de paie', required=True)
    date_from = fields.Date('Date de début', required=True)
    date_to = fields.Date('Date de fin', required=True)
    company_id= fields.Many2one('res.company', 'Compagnie', required=True, default=1)
    type_employe = fields.Selection([('mensuel','Mensuel'),
                                     ('journalier','Journalier'),
                                     ('horaire','Horaire'),('all','Tous les employés')],"Livre de paie pour:", default="all")


    def _lines(self, date_from, date_to, company_id, type_employe):
        res = {}
        resultats = []
        _headers = ['NOM ET PRENOMS']
        rules = self.env['hr.salary.rule'].search([('appears_on_payroll', '=', True)])
        emp_obj = self.env['hr.employee']
        date_from = date_from
        date_to = date_to
        print ("---------------------------------------------------------------------------------------------------------")
        for rule in rules :
            print(rule.name)
            _headers.append(rule.name)
        print ("---------------------------------------------------------------------------------------------------------")
        self._codes_rules = rules.mapped(lambda r: r.code)
        res['codes'] = self._codes_rules
        res['headers'] = _headers
        self.env.cr.execute("SELECT id FROM hr_payslip WHERE (date_from between to_date(%s,'yyyy-mm-dd') AND "
            "to_date(%s,'yyyy-mm-dd')) AND (date_to between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd')) AND "
            "company_id = %s", (date_from, date_to, date_from, date_to, company_id ))
        payslip_ids = [x[0] for x in self._cr.fetchall()]
        if payslip_ids :
            #Trier les employés par type(mensuel, journalier, horaire ou tous les employés
            if type_employe == 'mensuel':
                payslips_sorted= self.env['hr.payslip'].browse(payslip_ids).sorted(key=lambda r: r.employee_id.name)
                payslips = payslips_sorted.filtered(lambda r: r.employee_id.type == 'm')
            if type_employe == 'journalier':
                payslips_sorted= self.env['hr.payslip'].browse(payslip_ids).sorted(key=lambda r: r.employee_id.name)
                payslips = payslips_sorted.filtered(lambda r: r.employee_id.type == 'j')
            if type_employe == 'horaire':
                payslips_sorted= self.env['hr.payslip'].browse(payslip_ids).sorted(key=lambda r: r.employee_id.name)
                payslips = payslips_sorted.filtered(lambda r: r.employee_id.type == 'h')
            if type_employe == 'all':
                payslips= self.env['hr.payslip'].browse(payslip_ids).sorted(key=lambda r: r.employee_id.name)
            print('!!!!!',payslips)
            for employee, lines in groupby(payslips, lambda l: l.employee_id):
                vals = {'NAME': employee.name, 'type': employee.type}
                print('!!!',vals)
                print(employee)
                slips = list(lines)
                for rule in self._codes_rules :
                    amount = 0.0
                    for slip in slips :
                        self.env.cr.execute("SELECT SUM(total) FROM hr_payslip_line WHERE slip_id=%s AND code=%s",
                                     (slip.id, rule))
                        result = self.env.cr.dictfetchall()
                        if result and result[0]['sum'] is None:
                            amount+= 0.0
                        else:
                            amount += result[0].get('sum')
                    print(amount)
                    vals[rule] = amount
                print(vals)
                resultats+=[vals]
        res['lines']= resultats
        print(res)
        return res

    def _lines_total(self, codes, lines):
        res = {}
        for code in codes :
            total = 0
            for line in lines :
                if line[code] is not None :
                    total+= line[code]
            res[code] = total
        return res

    def _print_report(self, data):
        data['form'].update(self.read(['initial_balance', 'sortby'])[0])
        if data['form'].get('initial_balance') and not data['form'].get('date_from'):
            raise UserError(_("You must define a Start Date"))

        records = self.env[data['model']].browse(data.get('ids', []))
        return self.env.ref('hr_payroll_ci_raport.report_hr_payroll').with_context(landscape=True).report_action(self, data=data)

    @api.multi
    def check_report(self):
        self.ensure_one()
        print(self.id)
        data = {}
        data['ids'] = self.id
        data['model'] = 'hr.payroll.payroll'
        data['form'] = self.read(['name','date_from', 'date_to', 'company_id','type_employe'])[0]
        print(data)
        return self._print_report(data)

    @api.multi
    def export_xls(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'hr.pauroll.payroll'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]

        return self.env.ref('hr_payroll_ci_raport.payroll_report_xlsx').report_action(self, data=datas,  config=False)



