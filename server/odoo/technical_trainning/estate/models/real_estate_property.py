from odoo import fields, models


class RealEstateProperty(models.Model):
    _name = "real.estate.property"
    _description = "Real Estate property Management"


    name= fields.Char(string="Name", default="House", required=True)
    description = fields.Text(string= "Description")
    postcode = fields.Char(string="Postcode")
    date_availability = fields.Date(string="Dateavailability")
    expected_price = fields.Float(string="Expected Price", required=True)
    selling_price = fields.Float(string="Selling Price")
    bedrooms = fields.Integer (string="Number of bedrooms")
    living_area = fields.Integer (string="Size of Room")
    facades = fields.Integer (string="Facades")
    garage= fields.Boolean (string="Garage")
    garden= fields.Boolean (string="Garden")
    garden_area=fields.Integer (string="Size of garden area")
    garden_orientation = fields.Selection([
    ('north', 'North'),
    ('south', 'South'),
    ('east', 'East'),
    ('west', 'West')
    ], string='Garden Orientation')
