from odoo import models, fields, _
from odoo.exceptions import UserError

class QualityCheckInherit(models.Model):
    _inherit = 'quality.check'

    multi_pictures = fields.One2many(
        'quality.check.picture', 'check_id', string='Pictures')

class QualityCheckPicture(models.Model):
    _name = 'quality.check.picture'
    _description = 'Quality Check Pictures'

    check_id = fields.Many2one('quality.check', string='Quality Check', ondelete='cascade')
    picture = fields.Binary('Picture', attachment=True)

class QualityCheckWizard(models.TransientModel):
    _inherit = 'quality.check.wizard'

    multi_pictures = fields.One2many(related='current_check_id.multi_pictures', readonly=False)
    current_check_id = fields.Many2one('quality.check', required=True)
    

    def do_pass(self):
        if self.test_type == 'picture' and not self.multi_pictures:
            raise UserError(_('You must provide a picture before validating'))
        self.current_check_id.do_pass()
        return self.action_generate_next_window()