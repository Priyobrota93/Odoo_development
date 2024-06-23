from odoo import models, fields,api
from odoo.exceptions import ValidationError

class TestInputForm(models.Model):
    _name = "hr_mobile_access_input"
    _description = "Portal Access Test"

    pg_db_host = fields.Char(string='Database Host', required=True)
    pg_db_name = fields.Char(string='Database Name', required=True)
    pg_db_user = fields.Char(string='Database User', required=True)
    pg_db_password = fields.Char(string='Database Password', required=True)



    @api.model
    def default_get(self, fields):
        res = super(TestInputForm, self).default_get(fields)
        latest_record = self.search([], order='id desc', limit=1)
        if latest_record:
            res.update({
                'pg_db_host': latest_record.pg_db_host,
                'pg_db_name': latest_record.pg_db_name,
                'pg_db_user': latest_record.pg_db_user,
                'pg_db_password': latest_record.pg_db_password,
            })
        return res
    

    @api.constrains('pg_db_host', 'pg_db_name', 'pg_db_user', 'pg_db_password')
    def _check_unique_input(self):
        for record in self:
            existing_record = self.search([
                ('pg_db_host', '=', record.pg_db_host),
                ('pg_db_name', '=', record.pg_db_name),
                ('pg_db_user', '=', record.pg_db_user),
                ('pg_db_password', '=', record.pg_db_password),
                ('id', '!=', record.id)
            ])
            if existing_record:
                raise ValidationError("A record with the same database credentials already exists.")

