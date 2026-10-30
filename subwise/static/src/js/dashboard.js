/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Component, useState, onWillStart, onMounted, onWillUnmount, xml } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

const COLORS = { active: "#2fb36d", draft: "#8a94a6", paused: "#f5a623", cancelled: "#e5484d" };

class SubwiseDashboard extends Component {
    static template = xml`
    <div class="sw-root" t-att-class="{'sw-dark': state.dark}">
      <header class="sw-header">
        <div>
          <h1>SubWise</h1>
          <p class="sw-sub">Subscription overview · live data</p>
        </div>
        <div class="sw-actions">
          <div class="sw-chips">
            <t t-foreach="[[7,'7D'],[30,'30D'],[90,'90D'],[365,'1Y']]" t-as="p" t-key="p[0]">
              <button class="sw-chip" t-att-class="{active: state.days === p[0]}"
                      t-on-click="() => this.setPeriod(p[0])"><t t-esc="p[1]"/></button>
            </t>
          </div>
          <button class="sw-icon" t-on-click="refresh" title="Refresh">⟳</button>
          <button class="sw-icon" t-on-click="toggleDark" title="Theme">◐</button>
        </div>
      </header>

      <div class="sw-quick">
        <button class="sw-btn" t-on-click="() => this.create('subwise.subscription','New Subscription')">＋ Subscription</button>
        <button class="sw-btn ghost" t-on-click="() => this.create('subwise.plan','New Plan')">＋ Plan</button>
        <button class="sw-btn ghost" t-on-click="() => this.create('subwise.discount','New Discount')">＋ Discount</button>
        <button class="sw-btn ghost" t-on-click="() => this.create('subwise.payment','New Payment')">＋ Payment</button>
      </div>

      <t t-if="state.loading">
        <div class="sw-grid"><div class="sw-skel" t-foreach="[1,2,3,4]" t-as="i" t-key="i"/></div>
      </t>
      <t t-else="">
        <section class="sw-grid">
          <div class="sw-card kpi" t-on-click="() => this.open('subwise.subscription','Active',[['state','=','active']])">
            <span>MRR</span><b><t t-esc="fmt(counter.mrr)"/></b><i class="bar a"/>
          </div>
          <div class="sw-card kpi" t-on-click="() => this.open('subwise.subscription','Active',[['state','=','active']])">
            <span>Active subscriptions</span><b><t t-esc="Math.round(counter.active)"/></b><i class="bar b"/>
          </div>
          <div class="sw-card kpi" t-on-click="() => this.open('subwise.payment','Paid',[['state','=','paid']])">
            <span>Revenue (period)</span><b><t t-esc="fmt(counter.revenue)"/></b><i class="bar c"/>
          </div>
          <div class="sw-card kpi" t-on-click="() => this.open('subwise.payment','Pending',[['state','=','pending']])">
            <span>Pending payments</span><b><t t-esc="Math.round(counter.pending)"/></b><i class="bar d"/>
          </div>
        </section>

        <section class="sw-row">
          <div class="sw-card wide">
            <h3>Revenue trend</h3>
            <svg viewBox="0 0 600 220" class="sw-chart">
              <t t-foreach="data.series" t-as="s" t-key="s_index">
                <rect class="sw-col" t-att-x="s_index * 50 + 8" t-att-width="34"
                      t-att-y="190 - barH(s.value)" t-att-height="barH(s.value)" rx="6"
                      t-on-mouseenter="() => state.tip = s" t-on-mouseleave="() => state.tip = null"/>
                <text class="sw-lbl" t-att-x="s_index * 50 + 25" y="212" text-anchor="middle"><t t-esc="s.label.split(' ')[0]"/></text>
              </t>
            </svg>
            <div class="sw-tip" t-att-class="{show: state.tip}">
              <t t-if="state.tip"><t t-esc="state.tip.label"/> · <b><t t-esc="fmt(state.tip.value)"/></b></t>
              <t t-else="">Hover a bar for details</t>
            </div>
          </div>

          <div class="sw-card">
            <h3>Status mix</h3>
            <svg viewBox="0 0 120 120" class="sw-donut">
              <circle cx="60" cy="60" r="44" fill="none" stroke="var(--sw-line)" stroke-width="16"/>
              <t t-foreach="slices()" t-as="sl" t-key="sl.key">
                <circle cx="60" cy="60" r="44" fill="none" t-att-stroke="sl.color"
                        t-att-stroke-width="state.hover === sl.key ? 22 : 16"
                        t-att-stroke-dasharray="sl.dash" t-att-stroke-dashoffset="sl.off"
                        transform="rotate(-90 60 60)" class="sw-slice"
                        t-on-click="() => this.open('subwise.subscription', sl.key, [['state','=',sl.key]])"/>
              </t>
              <text x="60" y="64" text-anchor="middle" class="sw-total"><t t-esc="total()"/></text>
            </svg>
            <ul class="sw-legend">
              <li t-foreach="slices()" t-as="sl" t-key="sl.key"
                  t-on-mouseenter="() => state.hover = sl.key" t-on-mouseleave="() => state.hover = null"
                  t-on-click="() => this.open('subwise.subscription', sl.key, [['state','=',sl.key]])">
                <span class="dot" t-att-style="'background:' + sl.color"/>
                <t t-esc="sl.key"/> <b><t t-esc="sl.value"/></b>
              </li>
            </ul>
          </div>
        </section>

        <section class="sw-card">
          <div class="sw-toolbar">
            <h3>Recent subscriptions</h3>
            <input class="sw-search" placeholder="Search customer, plan, reference…"
                   t-model="state.q"/>
            <div class="sw-chips">
              <t t-foreach="['all','active','draft','paused','cancelled']" t-as="f" t-key="f">
                <button class="sw-chip" t-att-class="{active: state.filter === f}"
                        t-on-click="() => state.filter = f"><t t-esc="f"/></button>
              </t>
            </div>
          </div>
          <div class="sw-table">
            <div class="sw-tr sw-th"><span>Ref</span><span>Customer</span><span>Plan</span><span>Status</span><span class="r">Amount</span></div>
            <t t-foreach="rows()" t-as="r" t-key="r.id">
              <div class="sw-tr" t-on-click="() => this.openRecord(r.id)">
                <span><t t-esc="r.name"/></span><span><t t-esc="r.customer"/></span>
                <span><t t-esc="r.plan"/></span>
                <span><em class="pill" t-att-class="'s-' + r.state"><t t-esc="r.state"/></em></span>
                <span class="r"><t t-esc="fmt(r.amount)"/></span>
              </div>
            </t>
            <div t-if="!rows().length" class="sw-empty">No subscriptions match your filters.</div>
          </div>
        </section>
      </t>
    </div>`;

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({ loading: true, days: 30, dark: false, tip: null, hover: null, q: "", filter: "all" });
        this.data = useState({ kpis: {}, status: {}, series: [], recent: [] });
        this.counter = useState({ mrr: 0, active: 0, revenue: 0, pending: 0 });
        onWillStart(() => this.load());
        onMounted(() => { this.timer = setInterval(() => this.load(true), 60000); });
        onWillUnmount(() => clearInterval(this.timer));
    }

    async load(silent = false) {
        if (!silent) this.state.loading = true;
        const res = await this.orm.call("subwise.dashboard", "get_data", [this.state.days]);
        Object.assign(this.data, res);
        this.state.loading = false;
        this.animate(res.kpis);
    }

    animate(target) {
        const from = { ...this.counter }, t0 = performance.now(), dur = 700;
        const tick = (now) => {
            const k = Math.min((now - t0) / dur, 1), e = 1 - Math.pow(1 - k, 3);
            for (const key of Object.keys(target)) this.counter[key] = from[key] + (target[key] - from[key]) * e;
            if (k < 1) requestAnimationFrame(tick);
        };
        requestAnimationFrame(tick);
    }

    setPeriod(d) { this.state.days = d; this.load(); }
    refresh() { this.load(); }
    toggleDark() { this.state.dark = !this.state.dark; }
    fmt(v) { return "₹" + Math.round(v || 0).toLocaleString("en-IN"); }
    barH(v) {
        const max = Math.max(...this.data.series.map((s) => s.value), 1);
        return Math.max((v / max) * 170, 3);
    }
    total() { return Object.values(this.data.status).reduce((a, b) => a + b, 0); }
    slices() {
        const C = 2 * Math.PI * 44, tot = this.total() || 1;
        let acc = 0;
        return Object.entries(this.data.status).map(([key, value]) => {
            const len = (value / tot) * C, s = { key, value, color: COLORS[key],
                dash: `${len} ${C - len}`, off: -acc };
            acc += len;
            return s;
        });
    }
    rows() {
        const q = this.state.q.toLowerCase();
        return this.data.recent.filter((r) =>
            (this.state.filter === "all" || r.state === this.state.filter) &&
            [r.name, r.customer, r.plan].some((x) => (x || "").toLowerCase().includes(q)));
    }

    open(model, name, domain) {
        this.action.doAction({ type: "ir.actions.act_window", name, res_model: model,
            views: [[false, "list"], [false, "form"]], domain });
    }
    create(model, name) {
        this.action.doAction({ type: "ir.actions.act_window", name, res_model: model,
            views: [[false, "form"]], target: "current" });
    }
    openRecord(id) {
        this.action.doAction({ type: "ir.actions.act_window", res_model: "subwise.subscription",
            res_id: id, views: [[false, "form"]] });
    }
}

registry.category("actions").add("subwise_dashboard", SubwiseDashboard);