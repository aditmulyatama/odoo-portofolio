from odoo import models, fields, api, exceptions
from odoo.tools.float_utils import float_compare, float_is_zero

from datetime import timedelta

class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'Real Estate Property'
    _order = 'id desc'
    
    _sql_constraints = [
        ('check_expected_price', 'CHECK(expected_price >= 0)', 'The expected price must be positive.'),
        ('check_selling_price', 'CHECK(selling_price >= 0)', 'The selling price must be positive.'),
    ]
    
    active = fields.Boolean(default=True,)
    name = fields.Char(string='Title', required=True)
    description = fields.Text('Description')
    postcode = fields.Char('Postcode')
    date_availability = fields.Date('Available From',copy=False, default=lambda self: fields.Date.today()+timedelta(days=90))
    expected_price = fields.Float('Expected Price',required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer('Living Area (sqm)')
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer('Garden Area (sqm)')
    garden_orientation = fields.Selection(
        [('north', 'North'),
        ('south', 'South'),
        ('east', 'East'),
        ('west', 'West')],
        string='Garden Orientation')
    state = fields.Selection(
        [('new', 'New'),
        ('offer_received', 'Offer Received'),
        ('offer_accepted', 'Offer Accepted'),
        ('sold', 'Sold'),
        ('canceled', 'Canceled')],
        string='Status',
        default='new',
        required=True,
        )
    property_type_id = fields.Many2one('estate.property.type', string='Property Type')
    buyer = fields.Many2one('res.partner', string='Buyer', copy=False,readonly=True)
    salesperson = fields.Many2one('res.users', string='Salesperson', default=lambda self: self.env.user)
    tag_ids = fields.Many2many('estate.property.tag', string='Property Tags')
    offer_ids = fields.One2many('estate.property.offer', 'property_id', string='Offers')
    total_area = fields.Integer('Total Area (sqm)', readonly=True, compute='_compute_total_area')
    best_price = fields.Float('Best Price', compute='_compute_best_price')
    product_id = fields.Many2many('product.template', string='Products')
    
    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for rec in self:
            rec.total_area = rec.living_area + rec.garden_area
    
    @api.depends('offer_ids.price')
    def _compute_best_price(self):
        for rec in self:
            rec.best_price = 0
            if rec.offer_ids:
                rec.best_price = max(rec.offer_ids.mapped('price'))
                
    @api.onchange('garden')
    def _onchange_garden(self):
        if not self.garden:
            self.garden_area = 0
            self.garden_orientation = False
            
        else:
            self.garden_area = 10
            self.garden_orientation = 'north'
            
    def action_sold_state(self):
        for rec in self:
            if rec.state == 'canceled':
                raise exceptions.UserError('You cannot sell a canceled property.')
            rec.state = 'sold'
        return True
    
    def action_cancel_state(self):
        for rec in self:
            if rec.state == 'sold':
                raise exceptions.UserError('You cannot cancel a sold property.')
            rec.state = 'canceled'
        return True
    
    @api.constrains('expected_price', 'selling_price')
    def _check_selling_price(self):
        for property_record in self:
            if float_is_zero(property_record.expected_price, precision_digits=2):
                # If expected price is zero, skip the check
                continue
            
            if property_record.expected_price and property_record.selling_price == 0:
                continue
            
            lower_limit = property_record.expected_price * 0.9
            if float_compare(property_record.selling_price, lower_limit, precision_digits=2) == -1:
                raise exceptions.ValidationError("Selling price cannot be lower than 90% of the expected price.")
    
    @api.ondelete(at_uninstall=False)
    def _check_state_before_delete(self):
        for rec in self:
            if rec.state not in ['new', 'canceled']:
                raise exceptions.ValidationError('You cannot delete a property that is not new or canceled.')