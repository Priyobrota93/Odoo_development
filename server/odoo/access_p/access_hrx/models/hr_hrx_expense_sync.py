from odoo import models, fields, api
from odoo.exceptions import ValidationError
import psycopg2
import xmlrpc.client

class HrExpenseSync(models.Model):
    _name = 'hrx.expense.sync'
    _description = 'Expense Sync'

    hr_expense_id = fields.Many2one('hr.expense', string='HR Expense')
    hrx_expense_id = fields.Integer(string='HRX Expense ID')
    last_sync_date = fields.Datetime(string='Last Sync Date')

    def sync_expenses(self):

        pg_access = self.env['hr_mobile_access_input'].search([], order='id desc', limit=1)
        if not pg_access:
            print("No PostgreSQL access details found.")
            return

        PG_HOST = pg_access.pg_db_host
        PG_DB = pg_access.pg_db_name
        PG_USER = pg_access.pg_db_user
        PG_PASSWORD = pg_access.pg_db_password


        # url = 'localhost'
        # db = 'hrx_database'
       # username = 'postgres'
        # password = 'openpgpwd'
 
        common = xmlrpc.client.ServerProxy(f'http://{PG_HOST}/xmlrpc/2/common')
        uid = common.authenticate(PG_DB, PG_USER, PG_PASSWORD, {})
        models = xmlrpc.client.ServerProxy(f'http://{PG_HOST}/xmlrpc/2/object')

        # Sync from hr_expense to hrx_expense
        expenses = self.env['hr.expense'].search([('write_date', '>', self.last_sync_date)])
        for expense in expenses:
            vals = {
                'name': expense.name,
                'employee_id': expense.employee_id.id,
                'total_amount': expense.total_amount,
                # Add other fields as needed
            }
            sync_record = self.search([('hr_expense_id', '=', expense.id)], limit=1)
            if sync_record:
                # Update existing record
                models.execute_kw(PG_DB, uid, PG_PASSWORD, 'hrx.expense', 'write', [[sync_record.hrx_expense_id], vals])
            else:
                # Create new record
                hrx_expense_id = models.execute_kw(PG_DB, uid, PG_PASSWORD, 'hrx.expense', 'create', [vals])
                self.create({
                    'hr_expense_id': expense.id,
                    'hrx_expense_id': hrx_expense_id,
                    'last_sync_date': fields.Datetime.now(),
                })

        # Sync from hrx_expense to hr_expense
        hrx_expenses = models.execute_kw(PG_DB, uid, PG_PASSWORD, 'hrx.expense', 'search_read', [[['write_date', '>', self.last_sync_date]]])
        for hrx_expense in hrx_expenses:
            vals = {
                'name': hrx_expense['name'],
                'employee_id': hrx_expense['employee_id'][0],
                'total_amount': hrx_expense['total_amount'],
                # Add other fields as needed
            }
            sync_record = self.search([('hrx_expense_id', '=', hrx_expense['id'])], limit=1)
            if sync_record:
                # Update existing record
                sync_record.hr_expense_id.write(vals)
            else:
                # Create new record
                hr_expense = self.env['hr.expense'].create(vals)
                self.create({
                    'hr_expense_id': hr_expense.id,
                    'hrx_expense_id': hrx_expense['id'],
                    'last_sync_date': fields.Datetime.now(),
                })

        self.last_sync_date = fields.Datetime.now()

# class HrExpense(models.Model):
#     _inherit = 'hr.expense'

#     external_id = fields.Integer(string='External ID', unique=True, index=True)

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
#                 external_id = row[14]

#                 existing_expense = self.search([('external_id', '=', external_id)])
#                 if existing_expense:
#                     print(f"Expense with external_id {external_id} already exists. Skipping.")
#                     continue

#                 employee = self.env['hr.employee'].search([('id', '=', employee_id)], limit=1)
#                 if not employee:
#                     print(f"Employee with ID {id} not found. Skipping expense with id {id}.")
#                     continue

#                 expense_sheet = self.env['hr.expense.sheet'].search([('id', '=', sheet_id)], limit=1)
#                 if not expense_sheet:
#                     print(f"Expense sheet with ID {sheet_id} not found. Creating a new one.")
#                     expense_sheet = self.env['hr.expense.sheet'].create({
#                         'name': name,
#                         'employee_id': employee.id,
#                         'state': 'draft',
#                     })
#                     sheet_id = expense_sheet.id

#                 try:
#                     self.create({
#                         'employee_id': employee.id,
#                         'name': name,
#                         'sheet_id': sheet_id,
#                         'state': state,
#                         'payment_mode': payment_mode,
#                         'date': date,
#                         'accounting_date': accounting_date,
#                         'description': description,
#                         'total_amount': total_amount,
#                         'create_date': create_date,
#                         'write_date': write_date,
#                         'external_id': external_id,
#                     })
#                     print(f"Inserted expense record with id {id} successfully.")
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

#     @api.model
#     def update_expense(self):
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
#             conn.autocommit = True
#             cursor = conn.cursor()

#             expenses = self.search([])
#             for expense in expenses:
#                 cursor.execute("""
#                     UPDATE hrx_expense
#                     SET state = %s, name = %s, payment_mode = %s, accounting_date = %s
#                     WHERE external_id = %s
#                 """, (
#                     expense.state,
#                     expense.name,
#                     expense.payment_mode,
#                     expense.accounting_date,
#                     expense.external_id
#                 ))
#                 print(f"Updated hrx_expense for external_id {expense.external_id}.")

#             print("Status update completed successfully.")

#         except psycopg2.Error as e:
#             print(f"PostgreSQL error: {e}")

#         finally:
#             if cursor:
#                 cursor.close()
#             if conn:
#                 conn.close()
#                 print("PostgreSQL connection closed.")
