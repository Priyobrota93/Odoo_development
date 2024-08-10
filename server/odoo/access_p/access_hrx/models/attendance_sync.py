from odoo import models, fields, api
import psycopg2
from datetime import datetime
from .pg_connection import get_pg_access, get_pg_connection

class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    attn_id = fields.Integer(string="Attendance ID", required=True, index=True, copy=False)
    attn_req_id = fields.Integer(string="Attendance Request ID")
    update = fields.Boolean(string="Update", default=False)

    @staticmethod
    def get_latest_create_date(odoo_cursor):
        odoo_cursor.execute("SELECT latest_create_date FROM sync_status WHERE id = 1")
        result = odoo_cursor.fetchone()
        print("latest_create_date", result)
        return result[0] if result else None

    @staticmethod
    def set_latest_create_date(odoo_cursor, new_latest_create_date):
        try:
            print(f"Updating latest_create_date to: {new_latest_create_date}")
            odoo_cursor.execute("""
                UPDATE sync_status 
                SET latest_create_date = %s 
                WHERE id = 1
            """, (new_latest_create_date,))
        except Exception as e:
            print(f"Error updating latest_create_date: {e}")

    @staticmethod
    def get_max_create_date(mobile_cursor):
        try:
            mobile_cursor.execute("SELECT MAX(create_date) FROM hrx_attendance")
            result = mobile_cursor.fetchone()
            print("Max create", result)
            return result[0] if result else None
        except Exception as e:
            print(f"Error fetching max create_date: {e}")
        return None

    @api.model
    def transfer_mobile_attendance_data(self):
        print("Start transfer_mobile_attendance_data")
        pg_access = get_pg_access(self.env)
        if not pg_access:
            print("Failed to get PostgreSQL access.")
            return

        conn = get_pg_connection(pg_access)
        if not conn:
            print("Failed to connect to PostgreSQL.")
            return

        odoo_cursor = None
        mobile_cursor = None

        try:
            odoo_conn = self.env.cr
            odoo_cursor = odoo_conn.cursor()
            mobile_cursor = conn.cursor()

            print("Get the latest create_date")
            latest_create_date = self.get_latest_create_date(odoo_cursor)
            print(f"Latest create_date from sync_status: {latest_create_date}")

            print("Get the latest update_date")
            if latest_create_date:
                query = """
                    SELECT *
                    FROM hrx_attendance
                    WHERE create_date > %s
                """
                mobile_cursor.execute(query, (latest_create_date,))
            else:
                query = """
                    SELECT *
                    FROM hrx_attendance
                """
                mobile_cursor.execute(query)

            rows = mobile_cursor.fetchall()
            print("Execute odoo_cursor")
            for row in rows:
                print(f"Row data: {row}")
                odoo_cursor.execute("""
                    INSERT INTO hr_attendance (employee_id, in_latitude, in_longitude, out_latitude, out_longitude, check_in, check_out, create_date, write_date, worked_hours, attn_id, attn_req_id, update)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (attn_id) DO UPDATE
                    SET employee_id = EXCLUDED.employee_id,
                        out_latitude = EXCLUDED.out_latitude,
                        out_longitude = EXCLUDED.out_longitude,
                        check_out = EXCLUDED.check_out,
                        create_date = EXCLUDED.create_date,
                        write_date = EXCLUDED.write_date,
                        worked_hours = EXCLUDED.worked_hours,
                        update = EXCLUDED.update
                """, row[1:])


            print("Update the latest create_date")
            new_latest_create_date = self.get_max_create_date(mobile_cursor)
            print(f"New latest_create_date from hrx_attendance: {new_latest_create_date}")
            self.set_latest_create_date(odoo_cursor, new_latest_create_date)

            print("Commit the transactions")
            odoo_conn.commit()
            conn.commit()

        except Exception as e:
            print(f"Error: {e}")
            if odoo_conn:
                odoo_conn.rollback()
            if conn:
                conn.rollback()
        finally:
            if odoo_cursor:
                odoo_cursor.close()
            if mobile_cursor:
                mobile_cursor.close()
            if conn:
                conn.close()
