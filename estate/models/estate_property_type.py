from odoo import models, fields, api

class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Estate Property Type'
    _order = 'sequence'

    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'Type name must be unique.')
    ]
    name = fields.Char(required=True)
    property_ids = fields.One2many('estate.property', 'property_type_id', string='Properties')
    sequence = fields.Integer('Sequence', default=10, help='Used to order property types. Higher is better.')
    offer_ids = fields.One2many('estate.property.offer', 'property_type_id', string='Offers')
    offer_count = fields.Integer('Offer Count', compute='_compute_offer_count')
    
    @api.depends('offer_ids')
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)
            
    def action_view_offers(self):
        return {
            'name': 'Offers',
            'type': 'ir.actions.act_window',
            'res_model': 'estate.property.offer',
            'view_mode': 'tree,form',
            'domain': [('property_type_id', '=', self.id)],
        }