from odoo import models, fields, api
import psycopg2
import logging
from .pg_connection import get_pg_access, get_pg_connection

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)

class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    es_id = fields.Integer(string='Expense Sheet ID', unique=True, index=True)

    @api.model
    def transfer_expense_sheet_data_from_postgres(self):
        _logger.info("Starting transfer_expense_sheet_data_from_postgres method")

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
            query = "SELECT * FROM hrx_expense_sheet"
            cursor.execute(query)
            records = cursor.fetchall()

            for row in records:
                es_id = row[14]
                _logger.info(f"Processing External Sheet ID: {es_id}")
                message_main_attachment_id = row[1] if row[1] else None
                user_id = row[3] if row[3] else None
                approval_state = row[6] if row[6] else None
                accounting_date = row[8] if row[8] else None
                approval_date = row[10] if row[10] else None
                total_amount = row[9] if row[9] else 0.0
                untaxed_amount = row[15] if len(row) > 15 else 0.0

                existing_sheet = self.search([('es_id', '=', es_id)])
                if existing_sheet:
                    _logger.info(f"Expense sheet with es_id {es_id} already exists. Updating record.")
                    try:
                        existing_sheet.write({
                            'message_main_attachment_id': message_main_attachment_id,
                            'employee_id': row[2],
                            'user_id': user_id,
                            'name': row[4],
                            'state': row[5],
                            'approval_state': approval_state,
                            'payment_state': row[7],
                            'accounting_date': accounting_date,
                            'total_amount': total_amount,
                            'approval_date': approval_date,
                            'create_date': row[11],
                            'write_date': row[12],
                            'untaxed_amount': untaxed_amount,
                        })
                        _logger.info(f"Updated expense sheet record with es_id {es_id} successfully.")
                    except Exception as e:
                        _logger.error(f"Failed to update expense sheet record with es_id {es_id}: {e}")
                else:
                    _logger.info(f"Inserting new expense sheet with es_id {es_id}.")
                    try:
                        self.create({
                            'message_main_attachment_id': message_main_attachment_id,
                            'employee_id': row[2],
                            'user_id': user_id,
                            'name': row[4],
                            'state': row[5],
                            'approval_state': approval_state,
                            'payment_state': row[7],
                            'accounting_date': accounting_date,
                            'total_amount': total_amount,
                            'approval_date': approval_date,
                            'create_date': row[11],
                            'write_date': row[12],
                            'es_id': es_id,
                            'untaxed_amount': untaxed_amount,
                        })
                        _logger.info(f"Inserted expense sheet record with es_id {es_id} successfully.")
                    except Exception as e:
                        _logger.error(f"Failed to insert expense sheet record with es_id {es_id}: {e}")

            _logger.info("Expense sheet data transfer completed successfully.")

        except psycopg2.Error as e:
            _logger.error(f"PostgreSQL error: {e}")
        except Exception as e:
            _logger.error(f"Unexpected error: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
                _logger.info("PostgreSQL connection closed.")

    # @api.model
    # def update_expense_sheet(self):
    #     _logger.info("Starting update_expense_sheet method")

    #     pg_access = self.env['hr_mobile_access_input'].search([], order='id desc', limit=1)
    #     if not pg_access:
    #         _logger.error("No PostgreSQL access details found.")
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

    #         expense_sheets = self.search([])
    #         # accounting_date = datetime.strptime(accounting_date.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
    #         for sheet in expense_sheets:
    #             accounting_date = sheet.accounting_date if sheet.accounting_date else None
    #             try:
    #                 cursor.execute("""
    #                     UPDATE hrx_expense_sheet
    #                     SET state = %s, approval_state = %s, payment_state = %s, 
    #                     accounting_date = %s
    #                     WHERE es_id = %s
    #                 """, (
    #                     sheet.state,
    #                     sheet.approval_state,
    #                     sheet.payment_state,
    #                     accounting_date,
    #                     sheet.es_id
    #                 ))
    #                 _logger.info(f"Updated hrx_expense_sheet for es_id {sheet.es_id}.")
    #             except psycopg2.Error as e:
    #                 _logger.error(f"Error updating hrx_expense_sheet for es_id {sheet.es_id}: {e}")

    #         _logger.info("Status update completed successfully.")

    #     except psycopg2.Error as e:
    #         _logger.error(f"PostgreSQL error: {e}")
    #     except Exception as e:
    #         _logger.error(f"Unexpected error: {e}")
    #     finally:
    #         if cursor:
    #             cursor.close()
    #         if conn:
    #             conn.close()
    #             _logger.info("PostgreSQL connection closed.")

# from odoo import models, fields, api
# from odoo.exceptions import ValidationError               
# import psycopg2

# class HrExpenseSheet(models.Model):
#     _inherit = 'hr.expense.sheet'

#     es_id = fields.Integer(string='External Sheet ID', unique=True)

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

#                 existing_expense_sheet = self.env['hr.expense.sheet'].search([('es_id', '=', id)], limit=1)
#                 if existing_expense_sheet:
#                     print(f"Expense sheet with es_id {id} already exists. Updating.")
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
#                     print(f"Employee with ID {employee_id} not found. Skipping expense sheet with es_id {id}.")
#                     continue

#                 try:
#                     self.env['hr.expense.sheet'].create({
#                         'es_id': id,
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
#                     print(f"Inserted expense sheet record with es_id {id} successfully.")
#                 except ValidationError as e:
#                     print(f"Failed to insert expense sheet record with es_id {id}: {e}")

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





