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

    