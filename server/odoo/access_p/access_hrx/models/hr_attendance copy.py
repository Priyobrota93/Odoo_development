from odoo import models, fields, api
from odoo.exceptions import ValidationError
import psycopg2
from psycopg2 import connect, OperationalError, Error as PsycopgError
from .pg_connection import get_pg_access, get_pg_connection


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    attn_id = fields.Integer(string="Attendance ID", required=True, index=True, copy=False)
    attn_req_id = fields.Integer(string="Attendance Request ID")
    update = fields.Boolean(string="Update", default=False)

    @api.model
    def transfer_mobile_attendance_data(self):
        pg_access = get_pg_access(self.env)
        if not pg_access:
            print("Failed to get PostgreSQL access.")
            return

        conn = get_pg_connection(pg_access)
        if not conn:
            print("Failed to connect to PostgreSQL.")
            return

        odoo_cursor = self.env.cr  # This is already a cursor object
        mobile_cursor = None
        try:
            mobile_cursor = conn.cursor()
            print("Get the latest create_date")
            latest_create_date = self.get_latest_create_date(odoo_cursor)
            print(f"Latest create_date from sync_status: {latest_create_date}")

            print("Get the latest records from PostgreSQL")
            if latest_create_date:
                print("Get the latest records from PostgreSQL")
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

                self.env['hr.attendance'].create({
                    'employee_id': employee_id,
                    'in_latitude': in_latitude,
                    'in_longitude': in_longitude,
                    'out_latitude': out_latitude,
                    'out_longitude': out_longitude,
                    'check_in': check_in,
                    'check_out': check_out,
                    'create_date': create_date,
                    'write_date': write_date,
                    'worked_hours': worked_hours,
                    'attn_id': attn_id,
                    'update': update,
                })
                print(f"Inserted attendance record id {id} successfully.")

            max_create_date = self.get_max_create_date(mobile_cursor)
            if max_create_date:
                self.set_latest_create_date(odoo_cursor, max_create_date)

        except psycopg2.Error as e:
            print(f"PostgreSQL error: {e}")
        
        finally:
            if mobile_cursor:
                mobile_cursor.close()
            if conn:
                conn.close()
                print("PostgreSQL connection closed.")




    @api.model
    def get_latest_create_date(self, odoo_cursor):
        try:
            odoo_cursor.execute("SELECT latest_create_date FROM sync_status WHERE id = 1")
            result = odoo_cursor.fetchone()
            print("latest_create_date", result)
            return result[0] if result else None
        except Exception as e:
            print(f"Error fetching latest_create_date: {e}")
            return None

    @api.model
    def set_latest_create_date(self, odoo_cursor, new_latest_create_date):
        try:
            print(f"Updating latest_create_date to: {new_latest_create_date}")
            odoo_cursor.execute("""
                UPDATE sync_status 
                SET latest_create_date = %s 
                WHERE id = 1
            """, (new_latest_create_date,))
        except Exception as e:
            print(f"Error updating latest_create_date: {e}")

    @api.model
    def get_max_create_date(self, mobile_cursor):
        try:
            mobile_cursor.execute("SELECT MAX(create_date) FROM hrx_attendance")
            result = mobile_cursor.fetchone()
            print("Max create_date", result)
            return result[0] if result else None
        except Exception as e:
            print(f"Error fetching max create_date: {e}")
            return None






        #     new_ids = set()
        #     odoo_records = {}

        #     for record in records:
        #         id = record[0]
        #         employee_id = record[1]
        #         in_latitude = record[2]
        #         in_longitude = record[3]
        #         out_latitude = record[4]
        #         out_longitude = record[5]
        #         check_in = record[6]
        #         check_out = record[7]
        #         create_date = record[8]
        #         write_date = record[9]
        #         worked_hours = record[10]
        #         attn_id = record[11]
        #         update = record[12]

        #         new_ids.add(attn_id)
        #         if attn_id in odoo_records:
        #             odoo_records[attn_id].update({
        #                 "out_latitude": out_latitude,
        #                 "out_longitude": out_longitude,
        #                 "check_out": check_out,
        #                 "write_date": write_date,
        #                 "worked_hours": worked_hours,
        #                 'update': update,
        #             })
                    
        #             print(f"Updated attendance record id {id} successfully.")
        #             continue
        #         else:
        #             odoo_records[attn_id] = {
        #                 'employee_id': employee_id,
        #                 'in_latitude': in_latitude,
        #                 'in_longitude': in_longitude,
        #                 "out_latitude": out_latitude,
        #                 "out_longitude": out_longitude,
        #                 'check_in': check_in,
        #                 'check_out': check_out,
        #                 'create_date': create_date,
        #                 'write_date': write_date,
        #                 'worked_hours': worked_hours,
        #                 'attn_id': attn_id,
        #                 'update': update,
                        
        #             }
        #             print(f"Inserted attendance record id {id} successfully.")

        #     existing_attendances = self.search([('attn_id', 'in', list(new_ids))])
        #     existing_attendance_ids = {record.attn_id for record in existing_attendances}

        #     updates = []
        #     creations = []
        #     for attn_id, data in odoo_records.items():
        #         if attn_id in existing_attendance_ids:
        #             updates.append((data, attn_id))
        #         else:
        #             creations.append(data)

        #     for data, attn_id in updates:
        #         existing_record = self.search([('attn_id', '=', attn_id)])
        #         if existing_record:
        #             existing_record.write(data)
        #             print(f"Updated attendance record id {attn_id} successfully.")
 
        #     if creations:
        #         for data in creations:
        #             existing_records = self.search([
        #                 ('employee_id', '=', data['employee_id']),
        #                 ('check_in', '=', data['check_in']),
        #                 ('check_out', '=', False)
        #             ])
        #             if not existing_records:
        #                 self.create(data)
        #                 print(f"Inserted attendance record id {data['attn_id']} successfully.")

        #     # records_to_delete = self.search([('attn_id', 'not in', list(new_ids))])
        #     # if records_to_delete:
        #     #     records_to_delete.unlink()
        #     #     print("Deleted records from Odoo that are no longer in PostgreSQL.")

        #     max_create_date = self.get_max_create_date(mobile_cursor)
        #     if max_create_date:
        #         self.set_latest_create_date(odoo_cursor, max_create_date)
        
        # except PsycopgError as e:
        #     print(f"PostgreSQL error: {e}")

        # finally:
        #     if mobile_cursor:
        #         mobile_cursor.close()
        #     if conn:
        #         conn.close()
        #         print("PostgreSQL connection closed.")

   


    # @api.model
    # def transfer_data_to_postgres(self):
    #     pg_access = get_pg_access(self.env)
    #     if not pg_access:
    #         print("Failed to get PostgreSQL access.")
    #         return

    #     conn = get_pg_connection(pg_access)
    #     if not conn:
    #         print("Failed to connect to PostgreSQL.")
    #         return

    #     cursor = conn.cursor()
    #     try:
    #         odoo_records = self.search([])

    #         for record in odoo_records:
    #             query = """
    #                 INSERT INTO hrx_attendance (employee_id, in_latitude, in_longitude, out_latitude, out_longitude, check_in, check_out, create_date, write_date, worked_hours, attn_id)
    #                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    #                 ON CONFLICT (attn_id) DO UPDATE SET
    #                     employee_id = EXCLUDED.employee_id,
    #                     in_latitude = EXCLUDED.in_latitude,
    #                     in_longitude = EXCLUDED.in_longitude,
    #                     out_latitude = EXCLUDED.out_latitude,
    #                     out_longitude = EXCLUDED.out_longitude,
    #                     check_in = EXCLUDED.check_in,
    #                     check_out = EXCLUDED.check_out,
    #                     create_date = EXCLUDED.create_date,
    #                     write_date = EXCLUDED.write_date,
    #                     worked_hours = EXCLUDED.worked_hours
    #             """
    #             values = (
    #                 record.employee_id.id,
    #                 record.in_latitude,
    #                 record.in_longitude,
    #                 record.out_latitude,
    #                 record.out_longitude,
    #                 record.check_in,
    #                 record.check_out,
    #                 record.create_date,
    #                 record.write_date,
    #                 record.worked_hours,
    #                 record.attn_id,
    #             )
    #             cursor.execute(query, values)

    #         conn.commit()
    #         print("Data transfer to PostgreSQL completed successfully.")

    #     except PsycopgError as e:
    #         print(f"PostgreSQL error: {e}")
    #         conn.rollback()

    #     finally:
    #         if cursor:
    #             cursor.close()
    #         if conn:
    #             conn.close()
    #             print("PostgreSQL connection closed.")

   

    # def _get_next_attn_id(self, cursor):
    #     cursor.execute("SELECT nextval('hrx_attendance_attn_id_seq')")
    #     return cursor.fetchone()[0]
    
    

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
