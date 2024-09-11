from odoo import models, fields

class EstateEstate(models.Model):
    _inherit = 'estate.property'

    rental_id = fields.One2many('estate.rental', 'estate_id', string='Rental Details')
    tenant_id = fields.Many2one(related='rental_id.tenant_id', readonly=True)
