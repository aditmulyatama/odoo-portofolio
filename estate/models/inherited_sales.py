from odoo import models, fields, api



class ProductTemplate(models.Model):
    _inherit = 'product.template'

    property_ids = fields.Many2many('estate.property', string='Properties Located in')
