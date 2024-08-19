from odoo import models, fields

class TestPortalRelation(models.Model):
    _name = "hr_test_portal_access"
    _description = "Portal Access Test"

    employee_id = fields.Many2one('hr.employee', string='Employee', ondelete='cascade', required=True)
    department_id = fields.Many2one('hr.department', string='Department')
    job_id = fields.Many2one('hr.job', string='Job Position')
    name = fields.Char(string='Name')
    job_title = fields.Char(string='Job Title')
    work_phone = fields.Char(string='Work Phone')
    work_email = fields.Char(string='Work Email')
    create_date = fields.Datetime(string='Created on')
    write_date = fields.Datetime(string='Last Updated on')
    password = fields.Char(string='Password')

 