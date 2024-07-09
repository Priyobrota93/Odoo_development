from odoo import fields, models, api
import psycopg2

class TestPortalAccess(models.Model):
    _inherit = 'hr.employee'

    mobile_access = fields.Boolean(string='Mobile Access', default=False)
    password = fields.Char(string='Password')

    @api.model
    def action_open_view_employee_list_my(self):
        action = self.env.ref('hr.open_view_employee_list_my').read()[0]
        action['domain'] = [('mobile_access', '=', True)]
        return action

    # @api.model
    # def transfer_mobile_access_employees(self):
    #     self.env['hr_test_portal_access'].search([]).unlink()
    #     employees = self.search([('mobile_access', '=', True)])
    #     for employee in employees:
    #         self.env['hr_test_portal_access'].create({
    #             'employee_id': employee.id,
    #             'department_id': employee.department_id.id,
    #             'job_id': employee.job_id.id,
    #             'name': employee.name,
    #             'job_title': employee.job_title,
    #             'work_phone': employee.work_phone,
    #             'work_email': employee.work_email,
    #             'create_date': employee.create_date,
    #             'write_date': employee.write_date,
    #         })

    # @api.model
    # def integrate_mobile_access(self):
    #     pg_access = self.env['hr_mobile_access_input'].search([], order='id desc', limit=1)
    #     print("PostgreSQL Access Data: ", pg_access)
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
    #         conn = psycopg2.connect(
    #             host=PG_HOST,
    #             database=PG_DB,
    #             user=PG_USER,
    #             password=PG_PASSWORD
    #         )
    #         conn.autocommit = True
    #         cursor = conn.cursor()

    #         NEW_TABLE = 'hrx_employee'

    #         create_table_query = f"""
    #         CREATE TABLE IF NOT EXISTS {NEW_TABLE} (
    #             id SERIAL PRIMARY KEY,
    #             employee_id INTEGER UNIQUE,
    #             name VARCHAR(255),
    #             work_phone VARCHAR(50),
    #             work_email VARCHAR(255),
    #             job_title VARCHAR(255),
    #             create_date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    #             write_date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    #             password VARCHAR(255)
    #         )
    #         """
    #         cursor.execute(create_table_query)
    #         print(f"Table {NEW_TABLE} created or verified successfully.")

    #         employees = self.search([('mobile_access', '=', True)])
    #         if not employees:
    #             print("No employees found with mobile access.")
    #         else:
    #             print(f"Found {len(employees)} employees with mobile access.")

    #         for employee in employees:
    #             cursor.execute("""
    #                 SELECT 1 FROM hrx_employee WHERE employee_id = %s
    #             """, (employee.id,))
    #             if cursor.fetchone():
    #                 # Update existing record if employee_id exists
    #                 update_query = """
    #                     UPDATE hrx_employee
    #                     SET name = %s,
    #                         work_phone = %s,
    #                         work_email = %s,
    #                         job_title = %s,
    #                         write_date = %s,
    #                         password = %s
    #                     WHERE employee_id = %s
    #                 """
    #                password = employee.password if hasattr(employee, 'password') else None
    #                 cursor.execute(update_query, (
    #                     employee.name,
    #                     employee.work_phone,
    #                     employee.work_email,
    #                     employee.job_title,
    #                     employee.write_date,
    #                     employee.password,
    #                     employee.id,
    #                 ))
    #                 print(f"Updated employee_id {employee.id} successfully.")
    #             else:
    #                 # Insert new record if employee_id does not exist
    #                 insert_query = """
    #                     INSERT INTO hrx_employee (
    #                         employee_id, name,
    #                         work_phone, work_email, job_title, create_date, write_date, password
    #                     ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    #                 """
    #                 password = employee.password if hasattr(employee, 'password') else None 
    #                 cursor.execute(insert_query, (
    #                     employee.id,
    #                     employee.name,
    #                     employee.work_phone,
    #                     employee.work_email,
    #                     employee.job_title,
    #                     employee.create_date,
    #                     employee.write_date,
    #                     employee.password,
    #                 ))
    #                 print(f"Inserted employee_id {employee.id} successfully.")

    #         print("Integration of mobile access data completed successfully.")

    #     except psycopg2.Error as e:
    #         print(f"Error: {e}")
    #     finally:
    #         if cursor:
    #             cursor.close()
    #         if conn:
    #             conn.close()
    #             print("PostgreSQL connection closed.")










    @api.model
    def integrate_mobile_access(self):
        pg_access = self.env['hr_mobile_access_input'].search([], order='id desc', limit=1)
        print("PostgreSQL Access Data: ", pg_access)
        if pg_access:
            PG_HOST = pg_access.pg_db_host
            PG_DB = pg_access.pg_db_name
            PG_USER = pg_access.pg_db_user
            PG_PASSWORD = pg_access.pg_db_password
        else:
            print("No PostgreSQL access details found.")
            return

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

            NEW_TABLE = 'hrx_employee'

            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {NEW_TABLE} (
                id SERIAL PRIMARY KEY,
                employee_id INTEGER UNIQUE,
                name VARCHAR(255),
                work_phone VARCHAR(50),
                work_email VARCHAR(255),
                job_title VARCHAR(255),
                create_date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                write_date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                password VARCHAR(255)
            )
            """
            cursor.execute(create_table_query)
            print(f"Table {NEW_TABLE} created successfully.")

            employees = self.search([('mobile_access', '=', True)])
            if not employees:
                print("No employees found with mobile access.")
            else:
                print(f"Found {len(employees)} employees with mobile access.")

            for employee in employees:
                cursor.execute("""
                    SELECT 1 FROM hrx_employee WHERE employee_id = %s
                """, (employee.id,))
                if cursor.fetchone():
                    print(f"Record with employee_id {employee.id} already exists. Skipping.")
                    continue

                password = employee.password if hasattr(employee, 'password') else None

                cursor.execute("""
                    INSERT INTO hrx_employee (
                        employee_id, name,
                        work_phone, work_email, job_title, create_date, write_date, password
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    employee.id,
                    employee.name,
                    employee.work_phone,
                    employee.work_email,
                    employee.job_title,
                    employee.create_date,
                    employee.write_date,
                    employee.password,
                ))
                print(f"Inserted employee_id {employee.id} successfully.")

            print("Integration of mobile access data completed successfully.")

        except psycopg2.Error as e:
            print(f"Error: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
                print("PostgreSQL connection closed.")

 

    # @api.model
    # def integrate_mobile_access_attendance(self):
    #     pg_access = self.env['hr_mobile_access_input'].search([], order='id desc', limit=1)
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
    #         NEW_TABLE = 'hr_mobile_attendance'
    #         create_table_query = f"""
    #         CREATE TABLE IF NOT EXISTS {NEW_TABLE} (
    #             id SERIAL PRIMARY KEY,
    #             employee_id INTEGER NOT NULL,
    #             in_latitude NUMERIC,
    #             in_longitude NUMERIC,
    #             out_latitude NUMERIC,
    #             out_longitude NUMERIC,
    #             check_in TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    #             check_out TIMESTAMP WITHOUT TIME ZONE,
    #             create_date TIMESTAMP WITHOUT TIME ZONE,
    #             write_date TIMESTAMP WITHOUT TIME ZONE,
    #             attn_id serial UNIQUE
    #         )
    #         """
    #         cursor.execute(create_table_query)
    #         print(f"Table {NEW_TABLE} created successfully.")
    #         # cursor.execute("DELETE FROM hr_mobile_attendance_2")
            
    #         attendance_records = self.env['hr.attendance'].search([])
    #         if not attendance_records:
    #             print("No attendance records found.")
    #         else:
    #             print(f"Found {len(attendance_records)} attendance records.")

    #         for record in attendance_records:
    #             try:
    #                 cursor.execute("""
    #                 INSERT INTO hr_mobile_attendance (
    #                     id, employee_id, in_latitude,
    #                     in_longitude, out_latitude, out_longitude, check_in, check_out,
    #                     create_date, write_date
    #                 ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    #                 """, (
    #                     record.id,
    #                     record.employee_id.id,
    #                     record.in_latitude,
    #                     record.in_longitude,
    #                     record.out_latitude,
    #                     record.out_longitude,
    #                     record.check_in,
    #                     record.check_out,
    #                     record.create_date,
    #                     record.write_date
    #                 ))
    #                 print(f"Inserted attendance record id {record.id} successfully.")
    #             except psycopg2.Error as insert_error:
    #                 print(f"Failed to insert record id {record.id}: {insert_error}")

    #         print("Integration of hr_attendance data completed successfully.")
    #     except psycopg2.Error as e:
    #         print(f"Error: {e}")
    #     finally:
    #         if cursor:
    #             cursor.close()
    #         if conn:
    #             conn.close()
    #             print("PostgreSQL connection closed.")

 
                