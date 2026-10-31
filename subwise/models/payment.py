
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SubWisePayment(models.Model):
    _name = 'subwise.payment'
    _description = 'Subscription Payment'
    _order = 'payment_date desc'

    name = fields.Char(
        string='Payment Reference',
        default='New',
        readonly=True,
        copy=False
    )

    subscription_id = fields.Many2one(
        'subwise.subscription',
        string='Subscription',
        required=True,
        ondelete='cascade'
    )

    customer_id = fields.Many2one(
        'res.partner',
        string='Customer',
        related='subscription_id.customer_id',
        store=True
    )

    amount = fields.Float(
        string='Payment Amount',
        required=True
    )

    payment_date = fields.Date(
        string='Payment Date',
        default=fields.Date.today
    )

    payment_method = fields.Selection(
        [
            ('cash', 'Cash'),
            ('card', 'Card'),
            ('upi', 'UPI'),
            ('bank', 'Bank Transfer')
        ],
        string='Payment Method',
        required=True
    )

    transaction_reference = fields.Char(
        string='Transaction Reference'
    )

    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('paid', 'Paid'),
            ('failed', 'Failed')
        ],
        string='Payment Status',
        default='draft'
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals.get('name') == 'New':
                vals['name'] = (
                    self.env['ir.sequence'].next_by_code(
                        'subwise.payment'
                    ) or 'New'
                )

        return super().create(vals_list)

    @api.constrains('amount')
    def _check_amount(self):
        for record in self:
            if record.amount <= 0:
                raise ValidationError(
                    'Payment amount must be greater than zero.'
                )

    def action_mark_paid(self):
        self.write({'state': 'paid'})

    def action_mark_failed(self):
        self.write({'state': 'failed'})
