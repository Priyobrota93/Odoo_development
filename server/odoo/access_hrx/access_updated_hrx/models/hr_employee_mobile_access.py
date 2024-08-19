from odoo import fields, models, api
import psycopg2

class TestPortalAccess(models.Model):
    _inherit = 'hr.employee'

    mobile_access = fields.Boolean(string='Mobile Access', default=False)
    password = fields.Char(string='Password')

    @api.model
    def action_open_view_employee_list_my(self):
        action = self.env.ref('hr.open_view_employee_list_my').read()[0]
        action['domain'] = [('mobile_access', '=', True)]
        return action


   
 