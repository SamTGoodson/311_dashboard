window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(feature) {
                const pct = feature.properties.rank ?? 0;

                let fillColor;

                if (pct <= 0) {
                    fillColor = "#f7fbff";
                } else if (pct <= 0.5) {
                    fillColor = "#deebf7";
                } else if (pct <= 0.75) {
                    fillColor = "#c6dbef";
                } else if (pct <= 0.9) {
                    fillColor = "#9ecae1";
                } else if (pct <= 0.95) {
                    fillColor = "#6baed6";
                } else if (pct <= 0.99) {
                    fillColor = "#3182bd";
                } else {
                    fillColor = "#08519c";
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