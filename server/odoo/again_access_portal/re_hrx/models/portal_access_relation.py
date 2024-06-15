from odoo import fields, models,api

class PortalAccessRelation(models.Model):
    _name = "hrx_re_portal_access"
    _description = "Portal Access"

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    name = fields.Char(string='Employee Name')
    job_title = fields.Char(string='Job Title')
    mobile_access = fields.Boolean(string='Mobile Access')
    work_email = fields.Char(string='Work Email')
    work_phone = fields.Char(string='Work Phone')
    # mobile_phone = fields.Char(string='Mobile Phone')

class Employee(models.Model):
    _inherit = 'hr.employee'
    @api.model
    def copy_mobile_access_employees(self):
        self.search([]).unlink()
        employees = self.env['hr.employee'].search([('mobile_access', '=', True)])

        for employee in employees:
             self.env['hrx_re_portal_access'].create({
                'employee_id': employee.id,
                'name': employee.name,
                'job_title': employee.job_id.name,
                'mobile_access': employee.mobile_access,
                'work_email': employee.work_email,
                'work_phone': employee.work_phone,
                # 'mobile_phone': employee.mobile_phone,

            })