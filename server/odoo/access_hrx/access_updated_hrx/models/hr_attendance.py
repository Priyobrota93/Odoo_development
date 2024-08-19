from odoo import models, fields, api
from odoo.exceptions import ValidationError
import psycopg2
from psycopg2 import connect, OperationalError, Error as PsycopgError
import logging
from contextlib import closing
import traceback

_logger = logging.getLogger(__name__)

class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    attn_id = fields.Integer(string="Attendance ID", required=True, index=True, copy=False)
    attn_req_id = fields.Integer(string="Attendance Request ID")
    
     

