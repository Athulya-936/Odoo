
from odoo import models, fields, api


class SubWiseProduct(models.Model):
    _name = 'subwise.product'
    _description = 'Subscription Product'
    _order = 'name'

    name = fields.Char(
        string='Product Name',
        required=True
    )

    description = fields.Text(
        string='Description'
    )

    price = fields.Float(
        string='Base Price',
        required=True,
        default=0.0
    )

    category = fields.Selection(
        [
            ('entertainment', 'Entertainment'),
            ('software', 'Software'),
            ('shopping', 'Shopping'),
            ('cloud', 'Cloud Services'),
            ('other', 'Other')
        ],
        string='Category',
        default='other'
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )

    plan_ids = fields.One2many(
        'subwise.plan',
        'product_id',
        string='Subscription Plans'
    )

    plan_count = fields.Integer(
        string='Number of Plans',
        compute='_compute_plan_count'
    )

    @api.depends('plan_ids')
    def _compute_plan_count(self):
        for record in self:
            record.plan_count = len(record.plan_ids)

    @api.constrains('price')
    def _check_price(self):
        for record in self:
            if record.price < 0:
                raise models.ValidationError(
                    'Product price cannot be negative.'
                )
