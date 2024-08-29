from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import date


class HospitalPatient(models.Model):
    _name = "hospital.patient.view"
    _description = "Patient Master"
    _inherit = "mail.thread"

    name = fields.Char(string="Name", required=True, tracking=True)
    image = fields.Image(string="Profile Image", max_width=128, max_height=128)
    date_of_birth = fields.Date(String ="DOB")
    age = fields.Integer(string="Age", compute="_compute_age", inverse="_inverse_age", store=True, tracking=True)
    is_child = fields.Boolean(string="Is Child ?", tracking=True)
    notes = fields.Text(string="Notes", tracking=True)
    gender = fields.Selection(
        [("male", "Male"), ("female", "Female"), ("others", "Others")],
        string="Gender",
        tracking=True,
    )

    capitalized_name = fields.Char(
        string="Capitalized Name", compute="_compute_capitalized_name", store=True
    )
    
    ref =fields.Char(string="Reference", default=lambda self: _('New'))

    doctor_id=fields.Many2one('hospital.doctor',string="Doctor")
    

    @api.depends("name")
    def _compute_capitalized_name(self):
        if self.name:
            self.capitalized_name = self.name.upper()
        else:
            self.capitalized_name = ""


    @api.depends("date_of_birth")
    def _compute_age(self):
        today = date.today()
        for record in self:
            if record.date_of_birth:
                birth_date = record.date_of_birth
                record.age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            else:
                record.age = 0

    @api.onchange("age")
    def _onchange_age(self):
        if self.age <= 10:
            self.is_child = True
        else:
            self.is_child = False

    @api.constrains("is_child", "age")
    def _check_child_age(self):
        for rec in self:
            if rec.is_child and rec.age == 0:
                raise ValidationError(_("Age has to be recorderd !"))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['ref'] = self.env['ir.sequence'].next_by_code('hospital.patient')
        result = super(HospitalPatient, self).create(vals_list)
        return result
        
