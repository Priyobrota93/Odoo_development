from odoo import fields, models,api

class TestPortalAccess(models.Model):
    _inherit = 'hr.employee'

    mobile_access = fields.Boolean(string='Mobile Access', default=False)


    @api.model
    def action_open_view_employee_list_my(self):
        action = self.env.ref('hr.open_view_employee_list_my').read()[0]
        action['domain'] = [('mobile_access', '=', True)]
        return action
    

    @api.model
    def transfer_mobile_access_employees(self):

        self.env['hr_test_portal_access'].search([]).unlink()
        
        employees = self.search([('mobile_access', '=', True)])
        for employee in employees:
            self.env['hr_test_portal_access'].create({
                'employee_id': employee.id,
                'department_id': employee.department_id.id,
                'job_id': employee.job_id.id,
                'name': employee.name,
                'job_title': employee.job_title,
                'work_phone': employee.work_phone,
                'work_email': employee.work_email,
                'create_date': employee.create_date,
                'write_date': employee.write_date,
                })