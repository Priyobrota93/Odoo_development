from odoo import models, fields, api
from odoo.exceptions import ValidationError
import psycopg2
from psycopg2 import connect, OperationalError, Error as PsycopgError
from .pg_connection import get_pg_access, get_pg_connection
import logging

_logger = logging.getLogger(__name__)

class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    attn_id = fields.Integer(string="Attendance ID", required=True, index=True, copy=False)
    attn_req_id = fields.Integer(string="Attendance Request ID")
    update = fields.Boolean(string="Update", default=False)

    @api.model
    def transfer_mobile_attendance_data(self):
        pg_access = get_pg_access(self.env)
        if not pg_access:
            _logger.info("Failed to get PostgreSQL access.")
            return

        conn = get_pg_connection(pg_access)
        if not conn:
            _logger.info("Failed to connect to PostgreSQL.")
            return

        odoo_cursor = self.env.cr  
        mobile_cursor = None
        try:
            mobile_cursor = conn.cursor()
            _logger.info("Fetching the latest create_date")
            latest_create_date = self.get_latest_create_date(odoo_cursor)
            latest_write_date = self.get_latest_write_date(odoo_cursor)
            _logger.info(f"Latest create_date from sync_status: {latest_create_date}")
            _logger.info(f"Latest write_date from sync_status: {latest_write_date}")

            if latest_create_date:
                query = """
                    SELECT *
                    FROM hrx_attendance
                    WHERE create_date > %s OR (update = TRUE)
                """
                mobile_cursor.execute(query, (latest_create_date,))
            else:
                query = "SELECT * FROM hrx_attendance"
                mobile_cursor.execute(query)

            records = mobile_cursor.fetchall()

            for record in records:
                id = record[0]
                employee_id = record[1]
                in_latitude = record[2]
                in_longitude = record[3]
                out_latitude = record[4]
                out_longitude = record[5]
                check_in = record[6]
                check_out = record[7]
                create_date = record[8]
                write_date = record[9]
                worked_hours = record[10]
                attn_id = record[11]
                update = record[12]

                existing_attendance = self.get_existing_attendance(odoo_cursor, attn_id)
                if existing_attendance:
                        odoo_cursor.execute("""
                            UPDATE hr_attendance
                            SET out_latitude = %s,
                                out_longitude = %s,
                                check_out = %s,
                                write_date = %s,
                                worked_hours = %s,
                                update = %s
                            WHERE id = %s
                        """, (
                            out_latitude,
                            out_longitude,
                            check_out,
                            write_date,
                            worked_hours,
                            False,  # update flag set to False
                            existing_attendance,
                        ))
                        _logger.info(f"Updated attendance record id {id} successfully.")
                        # max_write_date = self.get_max_write_date(mobile_cursor)

                        mobile_cursor.execute("UPDATE hrx_attendance SET update = FALSE WHERE attn_id = %s", (attn_id,))
                else:
                    self.env['hr.attendance'].create({
                        'employee_id': employee_id,
                        'in_latitude': in_latitude or 0.0,
                        'in_longitude': in_longitude or 0.0,
                        'out_latitude': out_latitude or 0.0,
                        'out_longitude': out_longitude or 0.0,
                        'check_in': check_in,
                        'check_out': check_out or None,
                        'create_date': create_date,
                        'write_date': write_date,
                        'worked_hours': worked_hours or 0.0,
                        'attn_id': attn_id,
                        'update': update,  
                    })

            max_create_date = self.get_max_create_date(mobile_cursor)
            max_write_date = self.get_max_write_date(mobile_cursor)

            if max_create_date or max_write_date:
                self.set_latest_dates(odoo_cursor, max_create_date, max_write_date)

            self.env.cr.commit()
        except psycopg2.Error as e:
            _logger.error(f"PostgreSQL error: {e}")
        
        finally:
            if mobile_cursor:
                conn.commit()  
                mobile_cursor.close()
            if conn:
                conn.close()
                _logger.info("PostgreSQL connection closed.")

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
    
    @api.model
    def get_existing_attendance(self, odoo_cursor, attn_id):
        try:
            odoo_cursor.execute("SELECT id FROM hr_attendance WHERE attn_id = %s LIMIT 1", (attn_id,))
            result = odoo_cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            _logger.error(f"Error fetching existing attendance: {e}")
            return None


# self.env['hr.attendance'].create({
                #     'employee_id': employee_id,
                #     'in_latitude': in_latitude or 0.0,
                #     'in_longitude': in_longitude or 0.0,
                #     'out_latitude': out_latitude or 0.0,
                #     'out_longitude': out_longitude or 0.0,
                #     'check_in': check_in,
                #     'check_out': check_out,
                #     'create_date': create_date,
                #     'write_date': write_date,
                #     'worked_hours': worked_hours or 0.0,
                #     'attn_id': attn_id,
                #     'update': update,  
                # })
                # print(f"Inserted attendance record id {id} successfully.")


 # print(f"Inserted attendance record id {id} successfully.")
                    # # Reset the update flag in the mobile database
                    # mobile_cursor.execute("UPDATE hrx_attendance SET update = FALSE WHERE attn_id = %s", (attn_id,))

            # # Update the latest create_date in sync_status
            # max_create_date = self.get_max_create_date(mobile_cursor)
            # if max_create_date:
            #     self.set_latest_create_date(odoo_cursor, max_create_date)
