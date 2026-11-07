import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("elblasy_fleet_gps_dashboard_tour", {
    steps: () => [
        { content: "KPI tiles render", trigger: ".o_gps_kpis .o_gps_kpi_distance .o_gps_kpi_value" },
        { content: "twelve KPIs", trigger: ".o_gps_kpis:has(.o_gps_kpi:nth-child(12))", run: () => console.log("12 kpis") },
        { content: "charts are drawn on canvases", trigger: ".o_gps_card_box .o_gps_chart canvas" },
        { content: "the trip table lists the trip", trigger: ".o_gps_table td:contains('Dash 1')" },
        { content: "switching to one vehicle keeps working", trigger: ".o_gps_select", run: "select 0" },
        { content: "range buttons", trigger: ".o_gps_seg button:contains('30')", run: "click" },
        { content: "30 days selected", trigger: ".o_gps_seg button.active:contains('30')" },
    ],
});
