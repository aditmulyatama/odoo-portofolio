from odoo import models, fields


class EstatePropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = 'Estate Property Tag'
    _order = 'name'

    # name must be unique
    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'Tag name must be unique.')
    ]
    
    name = fields.Char(required=True)
    color = fields.Integer('Color Index', default=0)
    