
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SubWiseSubscription(models.Model):
    _name = 'subwise.subscription'
    _description = 'Customer Subscription'
    _order = 'create_date desc'

    name = fields.Char(
        string='Subscription Reference',
        default='New',
        readonly=True,
        copy=False
    )

    customer_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True
    )

    start_date = fields.Date(
        string='Start Date',
        default=fields.Date.today,
        required=True
    )

    end_date = fields.Date(
        string='End Date'
    )

    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('active', 'Active'),
            ('paused', 'Paused'),
            ('cancelled', 'Cancelled'),
            ('expired', 'Expired')
        ],
        string='Status',
        default='draft',
        required=True
    )

    line_ids = fields.One2many(
        'subwise.subscription.line',
        'subscription_id',
        string='Subscription Lines'
    )

    discount_id = fields.Many2one(
        'subwise.discount',
        string='Discount'
    )

    payment_ids = fields.One2many(
        'subwise.payment',
        'subscription_id',
        string='Payments'
    )

    amount_untaxed = fields.Float(
        string='Subtotal',
        compute='_compute_amounts',
        store=True
    )

    discount_amount = fields.Float(
        string='Discount Amount',
        compute='_compute_amounts',
        store=True
    )

    amount_total = fields.Float(
        string='Total Amount',
        compute='_compute_amounts',
        store=True
    )

    payment_count = fields.Integer(
        string='Payment Count',
        compute='_compute_payment_count'
    )

    @api.depends(
        'line_ids.subtotal',
        'discount_id',
        'discount_id.discount_type',
        'discount_id.value'
    )
    def _compute_amounts(self):
        for record in self:
            subtotal = sum(record.line_ids.mapped('subtotal'))
            discount = 0.0

            if record.discount_id:
                if record.discount_id.discount_type == 'percentage':
                    discount = subtotal * (
                        record.discount_id.value / 100
                    )
                else:
                    discount = record.discount_id.value

            discount = min(discount, subtotal)

            record.amount_untaxed = subtotal
            record.discount_amount = discount
            record.amount_total = subtotal - discount

    @api.depends('payment_ids')
    def _compute_payment_count(self):
        for record in self:
            record.payment_count = len(record.payment_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals.get('name') == 'New':
                vals['name'] = (
                    self.env['ir.sequence'].next_by_code(
                        'subwise.subscription'
                    ) or 'New'
                )

        return super().create(vals_list)

    def action_activate(self):
        for record in self:
            if not record.line_ids:
                raise ValidationError(
                    'Add at least one subscription line before activation.'
                )
            record.state = 'active'

    def action_pause(self):
        self.write({'state': 'paused'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_set_draft(self):
        self.write({'state': 'draft'})
