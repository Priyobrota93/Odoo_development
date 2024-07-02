from odoo import models, fields, api
from odoo.exceptions import ValidationError
import psycopg2
from psycopg2 import connect, Error as PsycopgError

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'
    attn_id = fields.Char(string='Attendance ID', required=False, unique=True)
    attn_req_id = fields.Char(string='Attendance Request ID')
    status = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='Status', default='pending')

    @api.model
    def transfer_mobile_attendance_data(self):
        pg_access = self.env['hr_mobile_access_input'].search([], order='id desc', limit=1)
        if not pg_access:
            print("No PostgreSQL access details found.")
            return

        PG_HOST = pg_access.pg_db_host
        PG_DB = pg_access.pg_db_name
        PG_USER = pg_access.pg_db_user
        PG_PASSWORD = pg_access.pg_db_password

        conn = None
        cursor = None
        try:
            conn = connect(
                host=PG_HOST,
                database=PG_DB,
                user=PG_USER,
                password=PG_PASSWORD
            )

            cursor = conn.cursor()
            query = "SELECT * FROM hr_mobile_attendance"
            cursor.execute(query)
            records = cursor.fetchall()

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
                attn_id = record[10]

                existing_attendance_id = self.search([
                    ('attn_id', '=', attn_id),
                ])

                if existing_attendance_id:
                    continue

                try:
                    self.create({
                        'employee_id': employee_id,
                        'in_latitude': in_latitude,
                        'in_longitude': in_longitude,
                        'out_latitude': out_latitude,
                        'out_longitude': out_longitude,
                        'check_in': check_in,
                        'check_out': check_out,
                        'create_date': create_date,
                        'write_date': write_date,
                        'attn_id': attn_id,
                    })
                    print(f"Inserted attendance record id {id} successfully.")
                except ValidationError as e:
                    print(f"Failed to insert record id {id}: {e}")

            print("Data transfer completed successfully.")

        except PsycopgError as e:
            print(f"PostgreSQL error: {e}")

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
                print("PostgreSQL connection closed.")

    @api.model
    def transfer_mobile_attendance_request(self):
        pg_access = self.env['hr_mobile_access_input'].search([], order='id desc', limit=1)
        if not pg_access:
            print("No PostgreSQL access details found.")
            return

        PG_HOST = pg_access.pg_db_host
        PG_DB = pg_access.pg_db_name
        PG_USER = pg_access.pg_db_user
        PG_PASSWORD = pg_access.pg_db_password

        conn = None
        cursor = None
        try:
            conn = connect(
                host=PG_HOST,
                database=PG_DB,
                user=PG_USER,
                password=PG_PASSWORD
            )
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM hr_mobile_attendance_request")
            records = cursor.fetchall()

            for record in records:
                employee_id = record[1]
                attn_req_id = record[2]
                status = record[4]

                status_mapping = {
                    'Pending': 'pending',
                    'Approved': 'approved',
                    'Rejected': 'rejected'
                }
                status = status_mapping.get(status, status)

                existing_attendance_id = self.search([
                    ('attn_req_id', '=', attn_req_id),
                ])

                if existing_attendance_id:
                    continue

                try:
                    self.create({
                        'employee_id': employee_id,
                        'status': status,
                        'attn_req_id': attn_req_id,
                    })
                    print(f"Inserted attendance record id {attn_req_id} successfully.")
                except ValidationError as e:
                    print(f"Failed to insert record id {attn_req_id}: {e}")

            print("Data transfer completed successfully.")

        except PsycopgError as e:
            print(f"PostgreSQL error: {e}")

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
                print("PostgreSQL connection closed.")

    @api.model
    def action_hr_request_view(self):
        action = self.env.ref('access_hrx.action_hr_request_view').read()[0]
        action['domain'] = [('attn_req_id', '!=', False)]
        return action

    @api.model
    def update_attendance_status(self):
        pg_access = self.env['hr_mobile_access_input'].search([], order='id desc', limit=1)
        if not pg_access:
            print("No PostgreSQL access details found.")
            return

        PG_HOST = pg_access.pg_db_host
        PG_DB = pg_access.pg_db_name
        PG_USER = pg_access.pg_db_user
        PG_PASSWORD = pg_access.pg_db_password

        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(
                host=PG_HOST,
                database=PG_DB,
                user=PG_USER,
                password=PG_PASSWORD
            )
            conn.autocommit = True
            cursor = conn.cursor()

            attendance_records = self.search([])
            for record in attendance_records:
                cursor.execute("""
                    UPDATE hr_mobile_attendance_request
                    SET status = %s
                    WHERE attn_req_id = %s AND employee_id = %s
                """, (record.status, record.attn_req_id, record.employee_id.id))
                print(f"Updated status for attn_req_id {record.attn_req_id} and employee_id {record.employee_id.id} to {record.status}.")

            print("Status update completed successfully.")

        except psycopg2.Error as e:
            print(f"PostgreSQL error: {e}")

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
                print("PostgreSQL connection closed.")

    def action_pending(self):
        self.write({'status': 'pending'})

    def action_approved(self):
        self.write({'status': 'approved'})

    def action_rejected(self):
        self.write({'status': 'rejected'})
