export const GLOBAL = {
    server: "https://road2nowhere-api-219791393556.southamerica-east1.run.app",

    loadLocal: function() {
        localStorage["load_messages"] = localStorage["load_messages"] || 1;
    },

    load: function() {
        GLOBAL.loadLocal();
    }
};