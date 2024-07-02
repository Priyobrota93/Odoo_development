from odoo import models, api
import psycopg2

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'