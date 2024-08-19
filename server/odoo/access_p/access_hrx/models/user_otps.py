from odoo import models, fields, api
from odoo.exceptions import ValidationError
import psycopg2
from psycopg2 import connect, OperationalError, Error as PsycopgError
from .pg_connection import get_pg_access, get_pg_connection
import logging

_logger = logging.getLogger(__name__)

class HrAttendance(models.Model):
    _name = "hr.users.otps"

    user_name = fields.Char(string='User Name')
    otp = fields.Char(string='OTP')
    expired_at = fields.Datetime(string='Expiration Time')