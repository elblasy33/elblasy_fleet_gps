import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("elblasy_fleet_gps_playback_tour", {
    steps: () => [
        { content: "the device is chosen", trigger: ".o_gps_pb_bar select.o_gps_select:has(option:contains('PB 1'))" },
        { content: "controls and slider are there", trigger: ".o_gps_pb_panel .o_gps_pb_slider" },
        { content: "the speed chart is drawn", trigger: ".o_gps_pb_chart canvas" },
        { content: "the vehicle marker is on the map", trigger: ".o_gps_pb .o_gps_marker .o_gps_lbl:contains('PB 1')", run: () => console.log("marker ok") },
        { content: "pick the fastest speed", trigger: ".o_gps_pb_speed", run: "select 600" },
        { content: "play", trigger: ".o_gps_pb_play", run: "click" },
        { content: "pause shows while playing", trigger: ".o_gps_pb_play:has(.oi[data-icon='pause'])" },
        { content: "the time advances", trigger: ".o_gps_pb_time:not(:contains('—'))", run: () => console.log("time ok") },
        { content: "pause again", trigger: ".o_gps_pb_play", run: "click" },
        { content: "back to play icon", trigger: ".o_gps_pb_play:has(.oi[data-icon='play_arrow'])" },
        { content: "trip list offers the drive", trigger: ".o_gps_pb_bar select:has(option[value='-1'])", run: () => console.log("trips ok") },
    ],
});
