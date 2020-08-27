#-*- coding:utf-8 -*-

from odoo import api, models, fields, _


class Employee(models.Model):

    _inherit = "hr.employee"

    current_leave_state = fields.Selection(compute='_compute_leave_status', string="Current Leave Status",
       selection_add=[('technical','Technical'), ('not_technical','No Technical'), ('chef_service','Chef de service'),
                      ('crh','Chargé des RH'), ('chef_depart','Chef de departement'),('cdaf','RAF'),])


    def _get_remaining_leaves_legals(self):
        """ Helper to compute the remaining leaves for the current employees
            :returns dict where the key is the employee id, and the value is the remain leaves
        """
        self._cr.execute("""
            SELECT
                sum(h.number_of_days) AS days,
                h.employee_id
            FROM
                hr_holidays h
                join hr_holidays_status s ON (s.id=h.holiday_status_id)
            WHERE
                h.state='validate' AND
                s.limit=False AND
                h.employee_id in %s AND s.code='CONG'
            GROUP BY h.employee_id""", (tuple(self.ids),))
        return dict((row['employee_id'], row['days']) for row in self._cr.dictfetchall())

    @api.multi
    def _compute_remaining_leaves_legals(self):
        remaining = self._get_remaining_leaves_legals()
        print(remaining)
        for employee in self:
            employee.holidays_legal_leaves = remaining.get(employee.id, 0.0)



    holidays_legal_leaves= fields.Float(compute='_compute_remaining_leaves_legals', string='Congés légaux restants')