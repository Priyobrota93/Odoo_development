from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime
import psycopg2
from .pg_connection import get_pg_access, get_pg_connection

class HrAttendanceRequest(models.Model):
    _name = "hr.attendance.request"
    _description = "HR Attendance Request"

    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    attn_req_id = fields.Integer(string="Attendance Request ID", required=True, unique=True)
    request_date = fields.Datetime(string="Request Date")
    check_in = fields.Datetime(string='Check In')
    check_out = fields.Datetime(string='Check Out')
    status = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='Status', default='pending')
    reason = fields.Text(string="Reason")
    create_date = fields.Datetime(string='Creation Date', default=fields.Datetime.now)
    write_date = fields.Datetime(string='Last Modification Date', default=fields.Datetime.now)

    @api.model
    def transfer_data_from_postgres(self):
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
            query = "SELECT * FROM hrx_attendance_request"
            cursor.execute(query)
            records = cursor.fetchall()
            new_ids = []


            for row in records:
                id = row[0]
                employee_id = row[1]
                request_date = row[2]
                check_in = row[3]
                check_out = row[4]
                status = row[5].lower()
                reason = row [6]
                create_date = row[7] 
                write_date = row[8]
                attn_req_id = row[9]  


                status_mapping = {
                    'Pending': 'pending',
                    'Approved': 'approved',
                    'Rejected': 'rejected'
                }
                status = status_mapping.get(status, status)


                request_date = datetime.strptime(request_date.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')

                new_ids.append(attn_req_id)

                existing_attendance_id = self.search([
                    ('attn_req_id', '=', attn_req_id),
                ])

                if existing_attendance_id:
                    continue
                try:
                    self.create({
                        'employee_id': employee_id,
                        'attn_req_id': attn_req_id ,
                        'request_date': request_date,
                        'check_in': check_in,
                        'check_out': check_out,
                        'status': status,
                        'reason': reason,
                        'create_date': create_date,
                        'write_date': write_date,
                    })
                    print(f"Inserted attendance record id {id} successfully.")
                except ValidationError as e:
                    print(f"Failed to insert record id {id}: {e}")



            records_to_delete = self.search([('attn_req_id', 'not in', new_ids)])
            if records_to_delete:
                try:
                    records_to_delete.unlink()
                    print("Deleted records from Odoo that are no longer in PostgreSQL.")
                except ValidationError as e:
                    print(f"Failed to delete records: {e}")                             

            print("Data transferred successfully from PostgreSQL to Odoo.")

        except psycopg2.Error as e:
            print(f"Error: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
                print("PostgreSQL connection closed.")

    @api.model
    def action_hr_attendance_request_view(self):
        action = self.env.ref('access_hrx.action_hr_attendance_request_view').read()[0]
        action['domain'] = [('attn_req_id', '!=', False)]
        return action

    @api.model
    def update_attendance_status(self):
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
            conn.autocommit = True
            attendance_records = self.search([])
            for record in attendance_records:
                cursor.execute("""
                    UPDATE hrx_attendance_request
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
