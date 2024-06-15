from odoo import api, fields, models, _

class HospitalDoctor(models.Model):
    _name = "hospital.doctor"
    _description = "Dotor Records"
    _inherit = "mail.thread"

    name = fields.Char(string="Name", required=True, tracking=True)
 

    gender = fields.Selection(
        [("male", "Male"), ("female", "Female"), ("others", "Others")],
        string="Gender",
        tracking=True,
    )

    age = fields.Integer(string="Age", tracking=True)

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



    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['ref'] = self.env['ir.sequence'].next_by_code('hospital.doctor')
        result = super(HospitalDoctor, self).create(vals_list)
        return result


# from odoo import api, fields, models, _
# from odoo.exceptions import ValidationError


# class Hospitaldoctor(models.Model):
#     _name = "hospital .doctor"
#     _description = "Doctor Records"
#     _inherit = "mail.thread"

#     name = fields.Char(string="Name", required=True, tracking=True)
#     age = fields.Integer(string="Age", tracking=True)
#     notes = fields.Text(string="Notes", tracking=True)
#     gender = fields.Selection(
#         [("male", "Male"), ("female", "Female"), ("others", "Others")],
#         string="Gender",
#         tracking=True,
#     )

#     capitalized_name = fields.Char(
#         string="Capitalized Name", compute="_compute_capitalized_name", store=True
#     )
    
#     ref =fields.Char(string="Reference", default=lambda self: _('New'))
    

#     @api.depends("name")
#     def _compute_capitalized_name(self):
#         if self.name:
#             self.capitalized_name = self.name.upper()
#         else:
#             self.capitalized_name = ""

#     @api.onchange("age")
#     def _onchange_age(self):
#         if self.age <= 10:
#             self.is_child = True
#         else:
#             self.is_child = False

#     @api.constrains("is_child", "age")
#     def _check_child_age(self):
#         for rec in self:
#             if rec.is_child and rec.age == 0:
#                 raise ValidationError(_("Age has to be recorderd !"))

#     @api.model_create_multi
#     def create(self, vals_list):
#         for vals in vals_list:
#             vals['ref'] = self.env['ir.sequence'].next_by_code('hospital.doctor')
#         result = super(Hospitaldoctor, self).create(vals_list)
#         return result
#         # print(vals_list)
#         # for vals in vals_list:
#             # vals['gender'] = 'Female'
#         # return super(Hospitaldoctor, self).create(vals_list)
