from odoo import models, fields, api, exceptions, Command



class EstatePropertyInherit(models.Model):
    _inherit = 'estate.property'

    def action_sold_state(self):
        # import ipdb; ipdb.set_trace()  # noqa
        
        for property_record in self:
            if not property_record.buyer:
                raise exceptions.UserError('Cannot create invoice without a buyer.')
            
            commission = property_record.expected_price * 0.06
            
            invoice_vals={
                'partner_id':property_record.buyer.id,
                'move_type' : 'out_invoice',
                'invoice_line_ids':[
                    Command.create({
                        'name': '6% Commission',
                        'quantity': 1,
                        'price_unit': commission,
                    }),
                    Command.create({
                        'name': 'Administrative Fees',
                        'quantity': 1,
                        'price_unit': 100,
                    }),
                ]
            }
            self.env['account.move'].create(invoice_vals)
        
        return super(EstatePropertyInherit, self).action_sold_state()