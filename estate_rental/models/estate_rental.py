from odoo import models, fields, api
from odoo.exceptions import ValidationError

class EstateRental(models.Model):
    _name = 'estate.rental'
    _description = 'Estate Rental'

    estate_id = fields.Many2one('estate.property', string="Estate", required=True, ondelete='cascade')
    tenant_id = fields.Many2one('res.partner', string="Tenant", required=True)
    rental_start_date = fields.Date(string="Rental Start Date", required=True)
    rental_end_date = fields.Date(string="Rental End Date", required=True)

    @api.depends('tenant_id')
    def _compute_display_name(self):
        for record in self:
            record.display_name = record.tenant_id.name if record.tenant_id else 'Rental'

    display_name = fields.Char(string="Display Name", compute="_compute_display_name", store=False)


    # this is for checking if the rental period overlaps with an existing rental
    @api.constrains('rental_start_date', 'rental_end_date', 'estate_id')
    def _check_rental_overlap(self):
        for record in self:
            if record.rental_end_date < record.rental_start_date:
                raise ValidationError("The rental end date cannot be earlier than the start date.")
            
            overlapping_rentals = self.env['estate.rental'].search([
                ('estate_id', '=', record.estate_id.id),
                ('id', '!=', record.id),  # Exclude the current record
                ('rental_start_date', '<=', record.rental_end_date),
                ('rental_end_date', '>=', record.rental_start_date),
            ])
            if overlapping_rentals:
                raise ValidationError("The rental period overlaps with an existing rental for this estate.")

    # this is for checking if the estate is already rented by another tenant
    # @api.model
    # def create(self, vals):
    #     estate = self.env['estate.property'].browse(vals['estate_id'])
    #     if estate.rental_id:
    #         raise ValidationError("This estate is already rented by another tenant.")
    #     record = super(EstateRental, self).create(vals)
    #     estate.rental_id = record.id  # Link the estate to this rental record
    #     return record

    @api.model
    def create(self, vals):
        # Ensure that the estate is not already rented within the specified period
        record = super(EstateRental, self).create(vals)
        record._check_rental_overlap()
        # used for many2one fields, the record is not created but the field value is set to the new record
        # record.estate_id.rental_id = record.id  # Link the estate to this rental record
        return record
    
    def unlink(self):
        # used for many2one fields, the record is not deleted but the field value is set to False
        # for record in self:
        #     record.estate_id.rental_id = False  # Unlink the rental when the record is deleted
        return super(EstateRental, self).unlink()
