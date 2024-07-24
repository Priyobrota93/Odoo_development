from odoo import fields,models


class RealEstate(models.Model):
    _name = "real.estate"
    _description = "Real Estate Management"


    name= fields.Char(string="Name", default="House", requireed=True)
    price= fields.Float(string= "Price")