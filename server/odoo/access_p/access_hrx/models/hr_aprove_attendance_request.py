from odoo import models, fields, api
from odoo.exceptions import ValidationError
import psycopg2
from psycopg2 import connect, OperationalError, Error as PsycopgError
from .pg_connection import get_pg_access, get_pg_connection


class HrAttendance(models.Model):
    _inherit = "hr.attendance"


    @api.model
    def transfer_approved_attendance_data(self):
        pg_access = get_pg_access(self.env)
        if not pg_access:
            print("Failed to get PostgreSQL access.")
            return

        conn = get_pg_connection(pg_access)
        if not conn:
            print("Failed to connect to PostgreSQL.")
            return

        cursor = conn.cursor()
        try:
            query = "SELECT * FROM hrx_attendance_request WHERE status = 'approved'"
            cursor.execute(query)
            records = cursor.fetchall()

            for record in records:
                employee_id = record[1]
                check_in = record[3]
                check_out = record[4]
                create_date = record[7]
                write_date = record[8]
                attn_req_id = record[9]

                existing_attendance = self.search([("attn_req_id", "=", attn_req_id)])
                if existing_attendance:
                    continue

                worked_hours = (check_out - check_in).total_seconds() / 3600
                attn_id = self._get_next_attn_id(cursor)

                try:
                    self.create(
                        {
                            "employee_id": employee_id,
                            "check_in": check_in,
                            "check_out": check_out,
                            "create_date": create_date,
                            "write_date": write_date,
                            "worked_hours": worked_hours,
                            "attn_id": attn_id,
                            "attn_req_id": attn_req_id,
                        }
                    )
                    print(f"Inserted attendance record for request id {attn_req_id} successfully.")

                    # Insert attendance record in PostgreSQL
                    insert_query = """
                        INSERT INTO hrx_attendance (employee_id, check_in, check_out, create_date, write_date, worked_hours, attn_id, attn_req_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(
                        insert_query,
                        (
                            employee_id,
                            check_in,
                            check_out,
                            create_date,
                            write_date,
                            worked_hours,
                            attn_id,
                            attn_req_id,
                        ),
                    )
                except ValidationError as e:
                    print(f"Error creating attendance record: {e}")

            conn.commit()
            print("Transfer of approved attendance data completed successfully.")
        except PsycopgError as e:
            print(f"PostgreSQL error: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
                print("PostgreSQL connection closed.")


                
    def _get_next_attn_id(self, cursor):
        cursor.execute("SELECT COALESCE(MAX(attn_id), 0) FROM hr_attendance")
        max_attn_id = cursor.fetchone()[0]
        return max_attn_id + 1
    

  