from odoo import models, fields, api
from odoo.exceptions import ValidationError
import psycopg2

class HrExpense(models.Model):
    _inherit = 'hr.expense'

    external_id = fields.Integer(string='External ID', readonly=True)

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
                employee_id = row[0]
                name = row[1]
                sheet_id = row[2]
                state = row[3]
                payment_mode = row[4]
                expense_date = row[5]
                description = row[6]
                total_amount = row[7]
                create_date = row[8]
                write_date = row[9]
                external_id = row[10]
                
                

                existing_expense = self.search([('external_id', '=', external_id)])
                if existing_expense:
                    print(f"Expense with external_id {external_id} already exists. Skipping.")
                    continue

                employee = self.env['hr.employee'].search([('id', '=', employee_id)], limit=1)
                if not employee:
                    print(f"Employee with ID {employee_id} not found. Skipping expense with external_id {external_id}.")
                    continue

                try:
                    self.create({
                        'employee_id': employee.id,
                        'name': name,
                        'sheet_id': sheet_id,
                        'state': state,
                        'payment_mode': payment_mode,
                        'expense_date': expense_date,
                        'description': description,
                        'total_amount': total_amount,
                        'state': state,
                        'create_date': create_date,
                        'write_date': write_date,
                        'external_id': external_id,
                    })
                    print(f"Inserted expense record with external_id {external_id} successfully.")
                except ValidationError as e:
                    print(f"Failed to insert expense record with external_id {external_id}: {e}")

            print("Expense data transfer completed successfully.")

        except psycopg2.Error as e:
            print(f"PostgreSQL error: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
                print("PostgreSQL connection closed.")