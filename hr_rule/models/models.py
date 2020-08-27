# -*- coding: utf-8 -*-

from odoo import models, fields, api

class module1(models.Model):
	# _name = 'module1.module1'
	_inherit = 'hr.contract'
	
	res_company_id = fields.Many2one("res.company","Société", related ="employee_id.company_id")	

class module1_employe(models.Model):
	# _name = 'module1.module1'
	_inherit = 'hr.employee'

class module1_bulletin(models.Model):
	# _name = 'module1.module1'
	_inherit = 'hr.payslip'

class module1_departement(models.Model):
	# _name = 'module1.module1'
	_inherit = 'hr.department'



#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100
