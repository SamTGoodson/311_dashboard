window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(feature) {
                const pct = feature.properties.rank ?? 0;

                let fillColor;

                if (pct <= 0) {
                    fillColor = "#ffffcc";
                } else if (pct <= 0.5) {
                    fillColor = "#ffeda0";
                } else if (pct <= 0.75) {
                    fillColor = "#fed976";
                } else if (pct <= 0.9) {
                    fillColor = "#feb24c";
                } else if (pct <= 0.95) {
                    fillColor = "#fd8d3c";
                } else if (pct <= 0.99) {
                    fillColor = "#e31a1c";
                } else {
                    fillColor = "#b10026";
                }

                return {
                    fillColor: fillColor,
                    color: "white",
                    weight: 1,
                    fillOpacity: 0.75
                };
            }

            ,
        function1: function(feature, layer) {
            const board = feature.properties.NTA;
            const count = feature.properties.rolling_avg ?? 0;
            const rank = feature.properties.rank ?? 0;

            layer.bindPopup(
                "<b>Community Board:</b> " + board +
                "<br><b>Complaints:</b> " + count +
                "<br><b>Rank:</b> " + rank
            );
        }

    }
});