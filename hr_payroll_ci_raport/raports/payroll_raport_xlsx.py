# -*- coding:utf-8 -*-

import datetime


from odoo import models




class HrPayrollPayrollXlsx(models.AbstractModel):

    _name = 'report.hr_payroll_ci_raport.report_payroll_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    i = 0

    # Formattage pour les headers
    header_format = {
        'bold': 1,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'fg_color': 'gray',
        'text_wrap': 1
    }

    content_format = {
        'bold': 0,
        'border': 1,
        'align': 'left',
        'valign': 'vcenter',
        'fg_color': 'white'
    }

    amount_format= {
        'bold': 1,
        'border': 1,
        'align': 'right',
        'valign': 'vcenter',
        'num_format': '# ##0'
    }

    def formatSheet(self, sheet):
        sheet.set_column('A:A', 40)
        sheet.set_column('B:V', 15)

    def generateHeaders(self, sheet, headers, header_format):
        col = 0
        sheet.set_row(self.i, 30)
        for code in headers :
            sheet.write(self.i, col, code, header_format)
            col+=1
        self.i+=1
    def generateLines(self, sheet, lines, codes, amount_format, content_format):
        for line in lines :
            col = 0
            sheet.write(self.i, col, line['NAME'], content_format)
            for code in codes:
                col+=1
                sheet.write(self.i, col, line[code], amount_format)
            self.i+=1

    def generateLinesTotaux(self, sheet, totaux, codes, amount_format, content_format):
        col = 0
        sheet.write(self.i, col, 'TOTAUX', content_format)
        for code in codes:
            col+=1
            sheet.write(self.i, col, totaux[code], amount_format)
        self.i+=1

    #def generate_xlsx_report(self, workbook, data, partners):
    def generate_xlsx_report(self, workbook, data, lines):
        report_payroll_obj = self.env['report.hr_payroll_ci_raport.report_payroll']
        print(data)
        print(lines)
        #_lines(self, date_from, date_to, company_id, type_employe)
        results = report_payroll_obj._lines(lines.date_from, lines.date_to, lines.company_id.id, lines.type_employe)
        totaux = report_payroll_obj._lines_total(results['codes'], results['lines'])

        print(totaux)
        sheet = workbook.add_worksheet('LIVRE DE PAIE')
        bold = workbook.add_format({'bold': True})
        header_format = workbook.add_format(self.header_format)
        content_format = workbook.add_format(self.content_format)
        amount_format = workbook.add_format(self.amount_format)
        # self.formatSheet(sheet)
        title = 'LIVRE DE PAIE '
        sheet.write(0, 0, title, bold)
        self.formatSheet(sheet)
        self.i=3
        self.generateHeaders(sheet, results['headers'], header_format)
        self.generateLines(sheet, results['lines'], results['codes'], amount_format, content_format)
        self.generateLinesTotaux(sheet, totaux, results['codes'], amount_format, content_format)


# HrPayrollPayrollXlsx('report.hr_payroll_ci_raport.hr_payroll.xlsx', 'hr.payroll.payroll')
