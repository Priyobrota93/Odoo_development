# from odoo import models, fields, api
# from odoo.exceptions import ValidationError
# import psycopg2

# class HrExpenseSheet(models.Model):
#     _inherit = 'hr.expense.sheet'

#     external_sheet_id = fields.Integer(string='External Sheet ID', unique=True)

#     @api.model
#     def transfer_expense_sheet_data_from_postgres(self):
#         pg_access = self.env['hr_mobile_access_input'].search([], order='id desc', limit=1)
#         if not pg_access:
#             print("No PostgreSQL access details found.")
#             return

#         PG_HOST = pg_access.pg_db_host
#         PG_DB = pg_access.pg_db_name
#         PG_USER = pg_access.pg_db_user
#         PG_PASSWORD = pg_access.pg_db_password

#         conn = None
#         cursor = None

#         try:
#             conn = psycopg2.connect(
#                 host=PG_HOST,
#                 database=PG_DB,
#                 user=PG_USER,
#                 password=PG_PASSWORD
#             )
#             cursor = conn.cursor()
#             cursor.execute("SELECT * FROM hrx_expense_sheet")
#             records = cursor.fetchall()

#             for row in records:
#                 id = row[0]
#                 employee_id = row[2]
#                 name = row[4]
#                 state = row[5]
#                 approval_state = row[6]
#                 payment_state = row[7]
#                 accounting_date = row[8]
#                 total_amount = row[9]
#                 create_date = row[11]
#                 write_date = row[12]

#                 existing_expense_sheet = self.env['hr.expense.sheet'].search([('external_sheet_id', '=', id)], limit=1)
#                 if existing_expense_sheet:
#                     print(f"Expense sheet with external_sheet_id {id} already exists. Updating.")
#                     existing_expense_sheet.write({
#                         'employee_id': employee_id,
#                         'name': name,
#                         'state': state,
#                         'approval_state': approval_state,
#                         'payment_state': payment_state,
#                         'accounting_date': accounting_date,
#                         'total_amount': total_amount,
#                         'write_date': write_date,
#                     })
#                     continue

#                 employee = self.env['hr.employee'].search([('id', '=', employee_id)], limit=1)
#                 if not employee:
#                     print(f"Employee with ID {employee_id} not found. Skipping expense sheet with external_sheet_id {id}.")
#                     continue

#                 try:
#                     self.env['hr.expense.sheet'].create({
#                         'external_sheet_id': id,
#                         'employee_id': employee_id,
#                         'name': name,
#                         'state': state,
#                         'approval_state': approval_state,
#                         'payment_state': payment_state,
#                         'accounting_date': accounting_date,
#                         'total_amount': total_amount,
#                         'create_date': create_date,
#                         'write_date': write_date,
#                     })
#                     print(f"Inserted expense sheet record with external_sheet_id {id} successfully.")
#                 except ValidationError as e:
#                     print(f"Failed to insert expense sheet record with external_sheet_id {id}: {e}")

#             print("Expense sheet data transfer completed successfully.")

#         except psycopg2.Error as e:
#             print(f"PostgreSQL error: {e}")
#         finally:
#             if cursor:
#                 cursor.close()
#             if conn:
#                 conn.close()
#                 print("PostgreSQL connection closed.")
# #


from odoo import models, fields, api
from odoo.exceptions import ValidationError
import psycopg2

class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    external_sheet_id = fields.Integer(string='External Sheet ID',unique=True,index=True)

    @api.model
    def transfer_expense_sheet_data_from_postgres(self):
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
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM hrx_expense_sheet")
            records = cursor.fetchall()

            for row in records:
                id = row[0]
                employee_id = row[2]
                name = row[4]
                state = row[5]
                approval_state = row[6]
                payment_state = row[7]
                accounting_date = row[8]
                total_amount = row[9]
                create_date = row[11]
                write_date = row[12]
                external_sheet_id = row[13]

                existing_expense_sheet = self.search([('external_sheet_id', '=', external_sheet_id)], limit=1)
                if existing_expense_sheet:
                    print(f"Expense with external_sheet_id {external_sheet_id} already exists. Skipping.")
                    continue

                employee = self.env['hr.employee'].search([('id', '=', employee_id)], limit=1)
                if not employee:
                    print(f"Employee with ID {employee_id} not found. Skipping expense with external_id {id}.")
                    continue

                try:
                    self.create({
                        'employee_id': employee_id,
                        'name': name,
                        'state': state,
                        'approval_state': approval_state,
                        'payment_state': payment_state,
                        'accounting_date': accounting_date,
                        'total_amount': total_amount,
                        'create_date': create_date,
                        'write_date': write_date,
                        'external_sheet_id': external_sheet_id,
                    })
                    print(f"Inserted expense record with id {id} successfully.")
                except ValidationError as e:
                    print(f"Failed to insert expense record with external_id {id}: {e}")

            print("Expense data transfer completed successfully.")

        except psycopg2.Error as e:
            print(f"PostgreSQL error: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
                print("PostgreSQL connection closed.")


