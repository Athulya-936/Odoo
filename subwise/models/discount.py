
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SubWiseDiscount(models.Model):
    _name = 'subwise.discount'
    _description = 'Subscription Discount'

    name = fields.Char(
        string='Discount Name',
        required=True
    )

    code = fields.Char(
        string='Coupon Code',
        required=True,
        copy=False
    )

    discount_type = fields.Selection(
        [
            ('percentage', 'Percentage'),
            ('fixed', 'Fixed Amount')
        ],
        string='Discount Type',
        required=True,
        default='percentage'
    )

    value = fields.Float(
        string='Discount Value',
        required=True
    )

    start_date = fields.Date(
        string='Start Date'
    )

    end_date = fields.Date(
        string='End Date'
    )

    max_uses = fields.Integer(
        string='Maximum Uses',
        default=0
    )

    used_count = fields.Integer(
        string='Used Count',
        default=0
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )

    is_valid = fields.Boolean(
        string='Currently Valid',
        compute='_compute_is_valid'
    )

    _sql_constraints = [
        (
            'unique_discount_code',
            'unique(code)',
            'Discount code must be unique.'
        )
    ]

    @api.depends(
        'active',
        'start_date',
        'end_date',
        'max_uses',
        'used_count'
    )
    def _compute_is_valid(self):
        today = fields.Date.today()

        for record in self:
            valid = record.active

            if record.start_date and today < record.start_date:
                valid = False

            if record.end_date and today > record.end_date:
                valid = False

            if (
                record.max_uses > 0
                and record.used_count >= record.max_uses
            ):
                valid = False

            record.is_valid = valid

    @api.constrains('value', 'discount_type')
    def _check_discount_value(self):
        for record in self:
            if record.value <= 0:
                raise ValidationError(
                    'Discount value must be greater than zero.'
                )

            if (
                record.discount_type == 'percentage'
                and record.value > 100
            ):
                raise ValidationError(
                    'Percentage discount cannot exceed 100%.'
                )

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for record in self:
            if (
                record.start_date
                and record.end_date
                and record.end_date < record.start_date
            ):
                raise ValidationError(
                    'End date cannot be earlier than start date.'
                )
