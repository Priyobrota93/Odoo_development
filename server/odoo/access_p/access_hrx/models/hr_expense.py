from odoo import models, fields, api
from odoo.exceptions import ValidationError
import psycopg2

class HrExpense(models.Model):
    _inherit = 'hr.expense'

    external_id = fields.Integer(string='External ID',unique=True,index=True)



    @api.model
    def transfer_expense_data_from_postgres(self):
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
            query = "SELECT * FROM hrx_expense"
            cursor.execute(query)
            records = cursor.fetchall()

            for row in records:
                id = row[0]
                employee_id = row[2]
                sheet_id = row[3]
                name = row[5]
                state = row[6]
                payment_mode = row[7]
                date = row[8]
                accounting_date = row[9]
                description = row[10]
                total_amount = row[11]
                create_date = row[12]
                write_date = row[13]
                external_id = row[14]

                
                

                existing_expense = self.search([('external_id', '=', external_id)])
                if existing_expense:
                    print(f"Expense with external-id {external_id} already exists. Skipping.")
                    continue

                employee = self.env['hr.employee'].search([('id', '=', employee_id)], limit=1)
                if not employee:
                    print(f"Employee with ID {id} not found. Skipping expense with id {id}.")
                    continue
                
                expense_sheet = self.env['hr.expense.sheet'].search([('id', '=', sheet_id)], limit=1)
                if not expense_sheet:
                    print(f"Expense sheet with ID {sheet_id} not found. Creating a new one.")
                    expense_sheet = self.env['hr.expense.sheet'].create({
                        'name': f"Sheet for expense {name}",
                        'employee_id': employee.id,
                        'state': 'draft',
                    })
                    sheet_id = expense_sheet.id


                try:
                    self.create({
                        'employee_id': employee.id,
                        'name': name,
                        'sheet_id': sheet_id,
                        'state': state,
                        'payment_mode': payment_mode,
                        'date': date,
                        'accounting_date' : accounting_date,
                        'description': description,
                        'total_amount': total_amount,
                        'state': state,
                        'create_date': create_date,
                        'write_date': write_date,
                        'external_id': external_id,

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


# from odoo import models, fields, api
# from odoo.exceptions import ValidationError
# import psycopg2

# class HrExpense(models.Model):
#     _inherit = 'hr.expense'

#     external_id = fields.Integer(string='External ID')

   
#     @api.model
#     def transfer_expense_data_from_postgres(self):
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
#             query = "SELECT * FROM hrx_expense"
#             cursor.execute(query)
#             records = cursor.fetchall()

#             for row in records:
#                 id = row[0]
#                 employee_id = row[2]
#                 sheet_id = row[3]
#                 name = row[5]
#                 state = row[6]
#                 payment_mode = row[7]
#                 date = row[8]
#                 accounting_date = row[9]
#                 description = row[10]
#                 total_amount = row[11]
#                 create_date = row[12]
#                 write_date = row[13]

#                 existing_expense = self.search([('external_id', '=', sheet_id)], limit=1)
#                 if existing_expense:
#                     print(f"Expense with external_id {sheet_id} already exists. Updating.")
#                     existing_expense.write({
#                         'employee_id': employee_id,
#                         'name': name,
#                         'sheet_id': sheet_id,
#                         'state': state,
#                         'payment_mode': payment_mode,
#                         'date': date,
#                         'accounting_date': accounting_date,
#                         'description': description,
#                         'total_amount': total_amount,
#                         'write_date': write_date,
#                     })
#                     continue

#                 employee = self.env['hr.employee'].search([('id', '=', employee_id)], limit=1)
#                 if not employee:
#                     print(f"Employee with ID {employee_id} not found. Skipping expense with external_id {id}.")
#                     continue
                
#                 expense_sheet = self.env['hr.expense.sheet'].search([('external_id', '=', sheet_id)], limit=1)
#                 if not expense_sheet:
#                     print(f"Expense sheet with external_id {sheet_id} not found. Creating a new one.")
#                     expense_sheet = self.env['hr.expense.sheet'].create({
#                         'external_id': sheet_id,
#                         'name': f"Sheet for expense {name}",
#                         'employee_id': employee.id,
#                         'state': 'draft',
#                     })

#                 try:
#                     self.create({
#                         'external_id': sheet_id,
#                         'employee_id': employee.id,
#                         'name': name,
#                         'sheet_id': expense_sheet.id,
#                         'state': state,
#                         'payment_mode': payment_mode,
#                         'date': date,
#                         'accounting_date': accounting_date,
#                         'description': description,
#                         'total_amount': total_amount,
#                         'create_date': create_date,
#                         'write_date': write_date,
#                     })
#                     print(f"Inserted expense record with external_id {id} successfully.")
#                 except ValidationError as e:
#                     print(f"Failed to insert expense record with external_id {id}: {e}")

#             print("Expense data transfer completed successfully.")

#         except psycopg2.Error as e:
#             print(f"PostgreSQL error: {e}")
#         finally:
#             if cursor:
#                 cursor.close()
#             if conn:
#                 conn.close()
#                 print("PostgreSQL connection closed.")