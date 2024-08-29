from odoo import api, fields, models, _
from datetime import date

class HospitalDoctor(models.Model):
    _name = "hospital.doctor"
    _description = "Dotor Records"
    _inherit = "mail.thread"

    name = fields.Char(string="Name", required=True, tracking=True)
    image = fields.Image(string="Profile Image", max_width=128, max_height=128)

    gender = fields.Selection(
        [("male", "Male"), ("female", "Female"), ("others", "Others")],
        string="Gender",
        tracking=True,
    )

    date_of_birth = fields.Date(String ="DOB")
    age = fields.Integer(string="Age", compute="_compute_age", inverse="_inverse_age", store=True, tracking=True)

    ref =fields.Char(string="Reference", default=lambda self: _('New'))

    capitalized_name = fields.Char(
        string="Capitalized Name", compute="_compute_capitalized_name", store=True
    )


    @api.depends("name")
    def _compute_capitalized_name(self):
        for record in self:
            if record.name:
                record.capitalized_name = record.name.upper()
            else:
                record.capitalized_name = ""

     
    @api.depends("date_of_birth")
    def _compute_age(self):
        today = date.today()
        for record in self:
            if record.date_of_birth:
                birth_date = record.date_of_birth
                record.age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            else:
                record.age = 0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['ref'] = self.env['ir.sequence'].next_by_code('hospital.doctor')
        result = super(HospitalDoctor, self).create(vals_list)
        return result

 