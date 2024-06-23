from odoo import fields, models, api
import psycopg2

class TestPortalAccess(models.Model):
    _inherit = 'hr.employee'

    mobile_access = fields.Boolean(string='Mobile Access', default=False)

    @api.model
    def action_open_view_employee_list_my(self):
        action = self.env.ref('hr.open_view_employee_list_my').read()[0]
        action['domain'] = [('mobile_access', '=', True)]
        return action

    @api.model
    def transfer_mobile_access_employees(self):
        self.env['hr_test_portal_access'].search([]).unlink()
        employees = self.search([('mobile_access', '=', True)])
        for employee in employees:
            self.env['hr_test_portal_access'].create({
                'employee_id': employee.id,
                'department_id': employee.department_id.id,
                'job_id': employee.job_id.id,
                'name': employee.name,
                'job_title': employee.job_title,
                'work_phone': employee.work_phone,
                'work_email': employee.work_email,
                'create_date': employee.create_date,
                'write_date': employee.write_date,
            })






    @api.model
    def integrate_mobile_access(self):
        pg_access = self.env['hr_mobile_access_input'].search([], order='id asc', limit=1)
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

            NEW_TABLE = 'integrated_mobile_data'

            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {NEW_TABLE} (
                id SERIAL PRIMARY KEY,
                employee_id INTEGER UNIQUE,
                name VARCHAR(255),
                department_id INTEGER,
                job_id INTEGER,
                work_phone VARCHAR(50),
                work_email VARCHAR(255),
                create_date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                write_date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
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
                    SELECT 1 FROM integrated_mobile_data WHERE employee_id = %s
                """, (employee.id,))
                if cursor.fetchone():
                    print(f"Record with employee_id {employee.id} already exists. Skipping.")
                    continue

                cursor.execute("""
                    INSERT INTO integrated_mobile_data (
                        employee_id, department_id, job_id, name,
                        work_phone, work_email, create_date, write_date
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    employee.id,
                    employee.department_id.id if employee.department_id else None,
                    employee.job_id.id if employee.job_id else None,
                    employee.name,
                    employee.work_phone,
                    employee.work_email,
                    employee.create_date,
                    employee.write_date,
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

    #         NEW_TABLE = 'integrated_hr_attendance'

    #         create_table_query = f"""
    #         CREATE TABLE IF NOT EXISTS {NEW_TABLE} (
    #             id SERIAL PRIMARY KEY,
    #             employee_id INTEGER NOT NULL,
    #             create_uid INTEGER,
    #             write_uid INTEGER,
    #             in_country_name VARCHAR(255),
    #             in_city VARCHAR(255),
    #             in_ip_address VARCHAR(255),
    #             in_browser VARCHAR(255),
    #             in_mode VARCHAR(255),
    #             out_country_name VARCHAR(255),
    #             out_city VARCHAR(255),
    #             out_ip_address VARCHAR(255),
    #             out_browser VARCHAR(255),
    #             out_mode VARCHAR(255),
    #             in_latitude NUMERIC,
    #             in_longitude NUMERIC,
    #             out_latitude NUMERIC,
    #             out_longitude NUMERIC,
    #             check_in TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    #             check_out TIMESTAMP WITHOUT TIME ZONE,
    #             create_date TIMESTAMP WITHOUT TIME ZONE,
    #             write_date TIMESTAMP WITHOUT TIME ZONE,
    #             worked_hours DOUBLE PRECISION,
    #             overtime_hours DOUBLE PRECISION
    #         )
    #         """
    #         cursor.execute(create_table_query)
    #         print(f"Table {NEW_TABLE} created successfully.")

    #         # Fetch hr_attendance data from Odoo
    #         attendance_records = self.env['hr.attendance'].search([])
    #         if not attendance_records:
    #             print("No attendance records found.")
    #         else:
    #             print(f"Found {len(attendance_records)} attendance records.")

    #         for record in attendance_records:
    #             print(f"Processing record ID: {record.id}")
    #             data_to_insert = (
    #                 record.employee_id.id, 
    #                 record.create_uid.id if record.create_uid else None, 
    #                 record.write_uid.id if record.write_uid else None,
    #                 record.in_country_name if record.in_country_name else None,
    #                 record.in_city if record.in_city else None,
    #                 record.in_ip_address if record.in_ip_address else None,
    #                 record.in_browser if record.in_browser else None,
    #                 record.in_mode if record.in_mode else None,
    #                 record.out_country_name if record.out_country_name else None,
    #                 record.out_city if record.out_city else None,
    #                 record.out_ip_address if record.out_ip_address else None,
    #                 record.out_browser if record.out_browser else None,
    #                 record.out_mode if record.out_mode else None,
    #                 record.in_latitude if record.in_latitude else None,
    #                 record.in_longitude if record.in_longitude else None,
    #                 record.out_latitude if record.out_latitude else None,
    #                 record.out_longitude if record.out_longitude else None,
    #                 record.check_in, 
    #                 record.check_out if record.check_out else None, 
    #                 record.create_date if record.create_date else None, 
    #                 record.write_date if record.write_date else None, 
    #                 record.worked_hours if record.worked_hours else 0, 
    #                 record.overtime_hours if record.overtime_hours else 0
    #             )
    #             print(f"Data to insert: {data_to_insert}")
    #             cursor.execute("""
    #                 INSERT INTO integrated_hr_attendance (
    #                     employee_id, create_uid, write_uid, in_country_name,
    #                     in_city, in_ip_address, in_browser, in_mode, out_country_name,
    #                     out_city, out_ip_address, out_browser, out_mode, in_latitude,
    #                     in_longitude, out_latitude, out_longitude, check_in, check_out,
    #                     create_date, write_date, worked_hours, overtime_hours
    #                 ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    #             """, data_to_insert)
    #             print(f"Inserted attendance record id {record.id} successfully.")

    #         print("Integration of hr_attendance data completed successfully.")

    #     except psycopg2.Error as e:
    #         print(f"Database connection error: {e}")
    #         print(traceback.format_exc())
    #     finally:
    #         if cursor:
    #             cursor.close()
    #         if conn:
    #             conn.close()
    #             print("PostgreSQL connection closed.")


    @api.model
    def integrate_mobile_access_attendance(self):
        pg_access = self.env['hr_mobile_access_input'].search([], order='id asc', limit=1)
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
            NEW_TABLE = 'test_hr_attendance'
            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {NEW_TABLE} (
                id SERIAL PRIMARY KEY,
                employee_id INTEGER NOT NULL,
                create_uid INTEGER,
                write_uid INTEGER,
                in_country_name VARCHAR(255),
                in_city VARCHAR(255),
                in_ip_address VARCHAR(255),
                in_browser VARCHAR(255),
                in_mode VARCHAR(255),
                out_country_name VARCHAR(255),
                out_city VARCHAR(255),
                out_ip_address VARCHAR(255),
                out_browser VARCHAR(255),
                out_mode VARCHAR(255),
                in_latitude NUMERIC,
                in_longitude NUMERIC,
                out_latitude NUMERIC,
                out_longitude NUMERIC,
                check_in TIMESTAMP WITHOUT TIME ZONE NOT NULL,
                check_out TIMESTAMP WITHOUT TIME ZONE,
                create_date TIMESTAMP WITHOUT TIME ZONE,
                write_date TIMESTAMP WITHOUT TIME ZONE,
                worked_hours DOUBLE PRECISION,
                overtime_hours DOUBLE PRECISION
            )
            """
            cursor.execute(create_table_query)
            print(f"Table {NEW_TABLE} created successfully.")
            
            attendance_records = self.env['hr.attendance'].search([])
            if not attendance_records:
                print("No attendance records found.")
            else:
                print(f"Found {len(attendance_records)} attendance records.")

            for record in attendance_records:
                try:
                    cursor.execute("""
                    INSERT INTO test_hr_attendance (
                        id, employee_id, create_uid, write_uid, in_country_name,
                        in_city, in_ip_address, in_browser, in_mode, out_country_name,
                        out_city, out_ip_address, out_browser, out_mode, in_latitude,
                        in_longitude, out_latitude, out_longitude, check_in, check_out,
                        create_date, write_date, worked_hours, overtime_hours
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        record.id,
                        record.employee_id.id,
                        record.create_uid.id if record.create_uid else None,
                        record.write_uid.id if record.write_uid else None,
                        record.in_country_name,
                        record.in_city,
                        record.in_ip_address,
                        record.in_browser,
                        record.in_mode,
                        record.out_country_name,
                        record.out_city,
                        record.out_ip_address,
                        record.out_browser,
                        record.out_mode,
                        record.in_latitude,
                        record.in_longitude,
                        record.out_latitude,
                        record.out_longitude,
                        record.check_in,
                        record.check_out,
                        record.create_date,
                        record.write_date,
                        record.worked_hours,
                        record.overtime_hours
                    ))
                    print(f"Inserted attendance record id {record.id} successfully.")
                except psycopg2.Error as insert_error:
                    print(f"Failed to insert record id {record.id}: {insert_error}")

            print("Integration of hr_attendance data completed successfully.")
        except psycopg2.Error as e:
            print(f"Error: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
                print("PostgreSQL connection closed.")
                