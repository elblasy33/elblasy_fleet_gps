import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("elblasy_fleet_gps_map_tour", {
    steps: () => [
        { content: "list shows the three vehicles", trigger: ".o_gps_row:nth-child(3)" },
        { content: "moving vehicles come first (sorted by plate)", trigger: ".o_gps_row:first-child .o_gps_row_name:contains('CAR 3')" },
        { content: "the parked one is last", trigger: ".o_gps_row:last-child .o_gps_row_name:contains('PARK 2')" },
        { content: "speed shown for the moving ones", trigger: ".o_gps_row .o_gps_speed:contains('40')" },
        { content: "filter chips with counts", trigger: ".o_gps_chip.active .o_gps_chip_n:contains('3')" },
        { content: "search narrows the list", trigger: ".o_gps_search input", run: "edit PARK" },
        { content: "only one row left", trigger: ".o_gps_rows:has(.o_gps_row:only-child .o_gps_row_name:contains('PARK 2'))" },
        { content: "select it", trigger: ".o_gps_row", run: "click" },
        { content: "vehicle card opens", trigger: ".o_gps_card .o_gps_card_title b:contains('PARK 2')" },
        { content: "card shows battery", trigger: ".o_gps_card .o_gps_stats:contains('77%')" },
        { content: "marker is on the map", trigger: ".o_gps_marker .o_gps_ring", run: () => console.log("marker on the map") },
        { content: "close card", trigger: ".o_gps_card .o_gps_x", run: "click" },
        { content: "card gone", trigger: ".o_gps_map:not(:has(.o_gps_card))" },
    ],
});
