import { user } from "@web/core/user";

const RTL_PLUGIN = "/elblasy_fleet_gps/static/lib/maplibre/mapbox-gl-rtl-text.js";
export const mapLang = () => ((user.lang || document.documentElement.lang || "en").toLowerCase().startsWith("ar") ? "ar" : "en");

/** Without this plugin MapLibre draws Arabic letters one by one, unjoined and in the wrong order. Loaded once, only when needed. */
export function enableArabicShaping() {
    const gl = globalThis.maplibregl;
    if (gl && gl.getRTLTextPluginStatus?.() === "unavailable") {
        gl.setRTLTextPlugin(new URL(RTL_PLUGIN, location.origin).href, true).catch(() => {});
    }
}

export const hasWebGL = () => {
    try {
        const c = document.createElement("canvas");
        return !!(c.getContext("webgl2") || c.getContext("webgl"));
    } catch {
        return false;
    }
};



/**
 * Run `fn` (which adds sources / layers) as soon as the style JSON is there. `map.isStyleLoaded()` is no good for this: it
 * is false while any map tile is still downloading, so a layer drawn at that moment would silently never appear.
 */
export function withStyle(map, fn) {
    try {
        fn();
    } catch (e) {
        if (/not done loading/i.test(e?.message || "")) {
            map.once("styledata", () => withStyle(map, fn));
        } else {
            throw e;
        }
    }
}

/**
 * MapLibre opens the attribution box in full on every size; it then covers the legend and a quarter of a phone screen.
 * Keep it as the small (i) button: the credits stay one tap away, as the licences require.
 */
export function collapseAttribution(map) {
    const fold = () => {
        const el = map.getContainer().querySelector(".maplibregl-ctrl-attrib");
        el?.classList.remove("maplibregl-compact-show");
        el?.removeAttribute("open");
    };
    map.once("load", () => setTimeout(fold, 0));
    map.once("idle", fold);
}
