from datetime import timedelta
from odoo import api, fields, models


class SubwiseDashboard(models.AbstractModel):
    _name = "subwise.dashboard"
    _description = "SubWise Dashboard Data"

    @api.model
    def get_data(self, days=30):
        Sub = self.env["subwise.subscription"]
        Pay = self.env["subwise.payment"]
        today = fields.Date.context_today(self)
        start = today - timedelta(days=days)

        active = Sub.search([("state", "=", "active")])
        status = {s: Sub.search_count([("state", "=", s)])
                  for s in ("draft", "active", "paused", "cancelled")}

        payments = Pay.search([("state", "=", "paid"), ("date", ">=", start)])
        buckets = 12
        step = max(days // buckets, 1)
        series = []
        for i in range(buckets):
            b_start = start + timedelta(days=i * step)
            b_end = b_start + timedelta(days=step)
            total = sum(p.amount for p in payments if b_start <= p.date < b_end)
            series.append({"label": b_start.strftime("%d %b"), "value": total})

        recent = Sub.search([], order="id desc", limit=30)
        return {
            "kpis": {
                "mrr": sum(active.mapped("amount_total")),
                "active": status["active"],
                "revenue": sum(payments.mapped("amount")),
                "pending": Pay.search_count([("state", "=", "pending")]),
            },
            "status": status,
            "series": series,
            "recent": [{
                "id": s.id,
                "name": s.name,
                "customer": s.partner_id.name or "-",
                "plan": s.plan_id.display_name or "-",
                "state": s.state,
                "amount": s.amount_total,
            } for s in recent],
        }