
from odoo import models, fields, api


class SubWiseDashboard(models.TransientModel):
    _name = 'subwise.dashboard'
    _description = 'SubWise Dashboard'

    total_products = fields.Integer(
        string='Total Products',
        compute='_compute_dashboard'
    )

    total_plans = fields.Integer(
        string='Total Plans',
        compute='_compute_dashboard'
    )

    total_subscriptions = fields.Integer(
        string='Total Subscriptions',
        compute='_compute_dashboard'
    )

    active_subscriptions = fields.Integer(
        string='Active Subscriptions',
        compute='_compute_dashboard'
    )

    total_customers = fields.Integer(
        string='Total Customers',
        compute='_compute_dashboard'
    )

    total_revenue = fields.Float(
        string='Total Revenue',
        compute='_compute_dashboard'
    )

    @api.depends()
    def _compute_dashboard(self):
        Product = self.env['subwise.product']
        Plan = self.env['subwise.plan']
        Subscription = self.env['subwise.subscription']
        Payment = self.env['subwise.payment']

        for record in self:
            record.total_products = Product.search_count([])
            record.total_plans = Plan.search_count([])

            record.total_subscriptions = Subscription.search_count([])

            record.active_subscriptions = Subscription.search_count([
                ('state', '=', 'active')
            ])

            record.total_customers = Subscription.search_count([
                ('customer_id', '!=', False)
            ])

            paid_payments = Payment.search([
                ('state', '=', 'paid')
            ])

            record.total_revenue = sum(
                paid_payments.mapped('amount')
            )
