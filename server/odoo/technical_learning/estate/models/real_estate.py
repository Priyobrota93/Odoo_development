from odoo import fields, models

class RealEstate(models.Model):
    _name = "real.estate"
    _description = "Real Estate Management"

    active = fields.Boolean(default=True, invisible=True)
    name = fields.Char(string="Name", default="House", required=True)
    image = fields.Image(string="Profile Image", max_width=128, max_height=128)
    state = fields.Selection(
        [
            ("new", "New"),
            ("received", "Offer Received"),
            ("accepted", "Offer Accepted"),
            ("sold", "Sold"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        copy=False,
        default="new",
    )
    postcode = fields.Char()
    date_availability = fields.Date(string="Date Availability", default=fields.Date.today)
    expected_price = fields.Float(string="Expected Price", required=True)
    best_offer = fields.Float(string="Best Offer")
    selling_price = fields.Float(string="Selling Price")
    description = fields.Text(string="Description")
    bedrooms = fields.Integer(string="Number of bedrooms")
    living_area = fields.Integer(string="Size of Room")
    facades = fields.Integer(string="Facades")
    garage = fields.Boolean(string="Garage")
    garden = fields.Boolean(string="Garden")
    garden_orientation = fields.Selection(
        [
            ('north', 'North'),
            ('south', 'South'),
            ('east', 'East'),
            ('west', 'West'),
        ],
        string="Garden Orientation",
    )
    related_image = fields.Image(related="image", string="Related Profile Image", max_width=128, max_height=128)