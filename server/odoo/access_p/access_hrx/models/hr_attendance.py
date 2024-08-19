from odoo import models, fields, api
from odoo.exceptions import ValidationError
import psycopg2
from psycopg2 import connect, OperationalError, Error as PsycopgError
from .pg_connection import get_pg_access, get_pg_connection
import logging
from contextlib import closing
import traceback

_logger = logging.getLogger(__name__)

class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    attn_id = fields.Integer(string="Attendance ID", required=True, index=True, copy=False)
    attn_req_id = fields.Integer(string="Attendance Request ID")
    update = fields.Boolean(string="Update", default=False)
    mobile_create_date = fields.Datetime(string="Mobile Create Date")
    mobile_write_date = fields.Datetime(string="Mobile Write Date")

    @api.model
    def transfer_mobile_attendance_data(self):
        pg_access = get_pg_access(self.env)
        if not pg_access:
            _logger.error("Failed to get PostgreSQL access.")
            return

        with closing(get_pg_connection(pg_access)) as conn:
            if not conn:
                _logger.error("Failed to connect to PostgreSQL.")
                return

            with closing(conn.cursor()) as mobile_cursor:
                try:
                    latest_create_date = self.get_latest_create_date()
                    latest_write_date = self.get_latest_write_date()
                    _logger.info(f"Latest create_date from sync_status: {latest_create_date}")
                    _logger.info(f"Latest write_date from sync_status: {latest_write_date}")

                    query = """
                        SELECT *
                        FROM hrx_attendance
                        WHERE create_date > %s OR (write_date > %s AND update is TRUE)
                        ORDER BY create_date ASC
                    """
                    mobile_cursor.execute(query, (latest_create_date,))

                    records = mobile_cursor.fetchall()
                    _logger.info(f"Fetched {len(records)} records from mobile database")

                    for record in records:
                        id, employee_id, in_latitude, in_longitude, out_latitude, out_longitude, check_in, check_out, create_date, write_date, _, attn_id, update = record

                        try:
                            worked_hours = self.calculate_worked_hours(check_in, check_out)

                            existing_attendance = self.search([('attn_id', '=', attn_id)], limit=1)
                            if existing_attendance:
                                if update:
                                    existing_attendance.write({
                                        'out_latitude': out_latitude or 0.0,
                                        'out_longitude': out_longitude or 0.0,
                                        'check_out': check_out,
                                        'write_date': write_date,
                                        'worked_hours': worked_hours,
                                        'update': False,
                                        'mobile_write_date': write_date,
                                    })
                                    _logger.info(f"Updated attendance record id {id} successfully.")
                            else:
                                self.create({
                                    'employee_id': employee_id,
                                    'in_latitude': in_latitude or 0.0,
                                    'in_longitude': in_longitude or 0.0,
                                    'out_latitude': out_latitude or 0.0,
                                    'out_longitude': out_longitude or 0.0,
                                    'check_in': check_in,
                                    'check_out': check_out or None,
                                    'create_date': create_date,
                                    'write_date': write_date,
                                    'worked_hours': worked_hours,
                                    'attn_id': attn_id,
                                    'update': False,
                                    'mobile_create_date': create_date,
                                    'mobile_write_date': write_date,
                                })
                                _logger.info(f"Created new attendance record for attn_id {attn_id}")

                            mobile_cursor.execute("UPDATE hrx_attendance SET update = FALSE WHERE attn_id = %s", (attn_id,))
                            conn.commit()

                            self.env.cr.commit()
                        except Exception as e:
                            _logger.error(f"Error processing record {id}: {e}\n{traceback.format_exc()}")
                            self.env.cr.rollback()
                            conn.rollback()

                            max_create_date = self.get_max_create_date(mobile_cursor)
                            max_write_date = self.get_max_write_date(mobile_cursor)

                            if max_create_date or max_write_date:
                                self.set_latest_dates(max_create_date, max_write_date)

                            self.env.cr.commit()

                except psycopg2.Error as e:
                    _logger.error(f"PostgreSQL error: {e}\n{traceback.format_exc()}")
                    self.env.cr.rollback()
                    conn.rollback()

    @api.model
    def calculate_worked_hours(self, check_in, check_out):
        if check_in and check_out:
            delta = check_out - check_in
            return delta.total_seconds() / 3600
        return 0.0

    @api.model
    def get_latest_create_date(self, odoo_cursor):
        try:
            odoo_cursor.execute("SELECT latest_create_date FROM sync_status WHERE id = 1")
            result = odoo_cursor.fetchone()
            _logger.info("latest_create_date: %s", result)
            return result[0] if result else None
        except Exception as e:
            _logger.error(f"Error fetching latest_create_date: {e}")
            return None

    @api.model
    def get_max_create_date(self, mobile_cursor):
        try:
            mobile_cursor.execute("SELECT MAX(create_date) FROM hrx_attendance")
            result = mobile_cursor.fetchone()
            _logger.info("Max create_date: %s", result)
            return result[0] if result else None
        except Exception as e:
            _logger.error(f"Error fetching max_create_date: {e}")
            return None

    @api.model
    def get_latest_write_date(self, odoo_cursor):
        try:
            odoo_cursor.execute("SELECT latest_write_date FROM sync_status WHERE id = 1")
            result = odoo_cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            _logger.error(f"Error fetching latest_write_date: {e}")
            return None

    @api.model
    def get_max_write_date(self, mobile_cursor):
        try:
            mobile_cursor.execute("SELECT MAX(write_date) FROM hrx_attendance")
            result = mobile_cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            _logger.error(f"Error fetching max_write_date: {e}")
            return None

    @api.model
    def set_latest_dates(self, odoo_cursor, new_latest_create_date, new_latest_write_date):
        try:
            odoo_cursor.execute("""
                UPDATE sync_status 
                SET latest_create_date = %s, latest_write_date = %s 
                WHERE id = 1
            """, (new_latest_create_date, new_latest_write_date))
        except Exception as e:
            _logger.error(f"Error updating latest dates: {e}")