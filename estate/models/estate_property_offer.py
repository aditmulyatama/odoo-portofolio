from odoo import models, fields, api, exceptions
from datetime import timedelta
from odoo.tools.float_utils import float_compare, float_is_zero


class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Estate Property Offer'
    _sql_constraints = [
        ('check_price', 'CHECK(price >= 0)', 'The price must be positive.')
        ]
    _order = 'price desc'
    
    price = fields.Float()
    status = fields.Selection(
        [('refused', 'Refused'),
         ('accepted', 'Accepted')],
        copy=False,
        readonly=True,
        )
    partner_id = fields.Many2one('res.partner', string='Buyer', required=True)
    property_id = fields.Many2one('estate.property', string='Property', required=True)
    property_type_id = fields.Many2one(related='property_id.property_type_id', string='Property Type', store=True, readonly=True)
    validity = fields.Integer('Validity (days)', default=7)
    date_deadline = fields.Date(compute='_compute_date_deadline', inverse='_inverse_date_deadline', store=True, string='Deadline')

    @api.depends('create_date', 'validity')
    def _compute_date_deadline(self):
        for record in self:
            create_date = record.create_date or fields.Date.today()
            record.date_deadline = create_date + timedelta(days=record.validity)

    @api.onchange('date_deadline')
    def _onchange_date_deadline(self):
            if self.create_date and self.date_deadline:
                delta = self.date_deadline - self.create_date.date()
                self.validity = delta.days
            elif self.date_deadline:
                delta = self.date_deadline - fields.Date.today()
                self.validity = delta.days

    def _inverse_date_deadline(self):
        for record in self:
            if record.create_date and record.date_deadline:
                delta = record.date_deadline - record.create_date.date()
                record.validity = delta.days
            elif record.date_deadline:
                delta = record.date_deadline - fields.Date.today()
                record.validity = delta.days
            else:
                record.validity = 7  # Default validity if both create_date and date_deadline are not set
    
    def action_accept_status(self):
        for record in self:
            record.status = 'accepted'
            record.property_id.selling_price = record.price
            record.property_id.buyer = record.partner_id.id
            record.property_id.state = 'offer_accepted'
            other_offers = self.env['estate.property.offer'].search([('property_id', '=', record.property_id.id), ('id', '!=', record.id)])
            other_offers.write({'status': 'refused'})
        return True
    
    def action_refuse_status(self):
        for record in self:
            record.status = 'refused'
        return True
    
            
    @api.model
    def create(self, vals_list):
        property = self.env['estate.property'].browse(vals_list['property_id'])
        
        if property.offer_ids and vals_list['price'] < max(property.offer_ids.mapped('price')):
            raise exceptions.ValidationError('The offer price cannot be lower than an existing offer.')
        
        property.state = 'offer_received'
        
        return super().create(vals_list)