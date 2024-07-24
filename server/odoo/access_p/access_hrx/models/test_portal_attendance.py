from odoo import models, fields, api
from odoo.exceptions import ValidationError
import psycopg2
from psycopg2 import connect, Error as PsycopgError

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'
    attn_id = fields.Char(string='Attendance ID', required=False, unique=True)
    attn_req_id = fields.Char(string='Attendance Request ID')

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
            query = "SELECT * FROM hrx_attendance"
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
                worked_hours = record[10]
                attn_id = record[11]

                existing_attendance_id = self.search([
                    ('attn_id', '=', attn_id),
                    ('in_latitude', '=', '0.0000000'),
                    ('out_latitude', '=',  '0.0000000'),
                    ('in_longitude', '=', '0.0000000'),
                    ('out_longitude', '=', '0.0000000')
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
                        'worked_hours' : worked_hours,
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
    def transfer_approved_attendance_data(self):
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

                existing_attendance = self.search([
                    ('attn_req_id', '=', attn_req_id),
                ])

                if existing_attendance:
                    continue

                worked_hours = (check_out - check_in).total_seconds() / 3600

                try:
                    self.create({
                        'employee_id': employee_id,
                        'check_in': check_in,
                        'check_out': check_out,
                        'create_date': create_date,
                        'write_date': write_date,
                        'worked_hours': worked_hours,
                        'attn_req_id': attn_req_id,
                    })
                    print(f"Inserted attendance record for request id {attn_req_id} successfully.")
                except ValidationError as e:
                    print(f"Failed to insert record for request id {attn_req_id}: {e}")


                try:
                    insert_query = """
                        INSERT INTO hrx_attendance (employee_id, check_in, check_out, create_date, write_date,  worked_hours,attn_req_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_query, (employee_id, check_in, check_out, create_date, write_date, worked_hours,attn_req_id))
                    conn.commit()
                    print(f"Inserted attendance record for employee id {employee_id} in hr_attendance table.")
                except PsycopgError as e:
                    print(f"Failed to insert record for employee id {employee_id} in hr_attendance table: {e}")
                    conn.rollback()

            print("Data transfer completed successfully.")

        except PsycopgError as e:
            print(f"PostgreSQL error: {e}")

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
                print("PostgreSQL connection closed.")




    # @api.model
    # def transfer_approved_attendance_data(self):
    #     self.env['hr_attendance_request'].search([]).unlink()
    #     statuses = self.search([('status', '=', 'approved')])
    #     for record in statuses:
    #         self.env['hr_attendance'].create({
    #             'employee_id': record.id,
    #             'attn_req_id': record.attn_req_id,
    #             'check_in': record.check_in,
    #             'check_out': record.check_out,
    #             'create_date': record.create_date,
    #             'write_date': record.write_date,
    #         })



    # @api.model
    # def transfer_mobile_attendance_request(self):
    #     pg_access = self.env['hr_mobile_access_input'].search([], order='id desc', limit=1)
    #     if not pg_access:
    #         print("No PostgreSQL access details found.")
    #         return

    #     PG_HOST = pg_access.pg_db_host
    #     PG_DB = pg_access.pg_db_name
    #     PG_USER = pg_access.pg_db_user
    #     PG_PASSWORD = pg_access.pg_db_password

    #     conn = None
    #     cursor = None
    #     try:
    #         conn = connect(
    #             host=PG_HOST,
    #             database=PG_DB,
    #             user=PG_USER,
    #             password=PG_PASSWORD
    #         )
    #         cursor = conn.cursor()

    #         cursor.execute("SELECT * FROM hr_mobile_attendance_request")
    #         records = cursor.fetchall()

    #         for record in records:
    #             employee_id = record[1]
    #             attn_req_id = record[2]
    #             status = record[4]

    #             status_mapping = {
    #                 'Pending': 'pending',
    #                 'Approved': 'approved',
    #                 'Rejected': 'rejected'
    #             }
    #             status = status_mapping.get(status, status)

    #             existing_attendance_id = self.search([
    #                 ('attn_req_id', '=', attn_req_id),
    #             ])

    #             if existing_attendance_id:
    #                 continue

    #             try:
    #                 self.create({
    #                     'employee_id': employee_id,
    #                     'status': status,
    #                     'attn_req_id': attn_req_id,
    #                 })
    #                 print(f"Inserted attendance record id {attn_req_id} successfully.")
    #             except ValidationError as e:
    #                 print(f"Failed to insert record id {attn_req_id}: {e}")

    #         print("Data transfer completed successfully.")

    #     except PsycopgError as e:
    #         print(f"PostgreSQL error: {e}")

    #     finally:
    #         if cursor:
    #             cursor.close()
    #         if conn:
    #             conn.close()
    #             print("PostgreSQL connection closed.")

   

    


    # @api.model
    # def transfer_mobile_attendance_request(self):
    #     pg_access = self.env['hr_mobile_access_input'].search([], order='id asc', limit=1)
    #     print("PostgreSQL Access Data: ", pg_access)
    #     if pg_access:
    #         PG_HOST = pg_access.pg_db_host
    #         PG_DB = pg_access.pg_db_name
    #         PG_USER = pg_access.pg_db_user
    #         PG_PASSWORD = pg_access.pg_db_password
    #     else:
    #         print("No PostgreSQL access details found.")
    #         return

    #     conn = None
    #     cursor = None
    #     try:
    #         conn = psycopg2.connect(
    #             host=PG_HOST,
    #             database=PG_DB,
    #             user=PG_USER,
    #             password=PG_PASSWORD
    #         )
    #         conn.autocommit = True
    #         cursor = conn.cursor()
            
    #         NEW_TABLE = 'hr_mobile_attendance_request'
    #         create_table_query = f"""
    #         CREATE TABLE IF NOT EXISTS {NEW_TABLE} (
    #             id SERIAL PRIMARY KEY,
    #             employee_id INTEGER NOT NULL,
    #             attn_req_id SERIAL UNIQUE,
    #             request_date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    #             status VARCHAR(50),
    #             reason TEXT,
    #         )
    #         """
    #         cursor.execute(create_table_query)
    #         print(f"Table {NEW_TABLE} created successfully.")
            
    #         insert_data_query = """
    #         INSERT INTO hr_mobile_attendance_request (
    #             employee_id, status, reason
    #         ) VALUES (%s, %s, %s)
    #         """

    #         cursor.execute(insert_data_query)
            
    #         print("Inserted records into hr_mobile_attendance_request successfully.")

    #     except psycopg2.Error as e:
    #         print(f"Error: {e}")
    #     finally:
    #         if cursor:
    #             cursor.close()
    #         if conn:
    #             conn.close()
    #             print("PostgreSQL connection closed.")