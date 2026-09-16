window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(feature) {
            const count = feature.properties.count;

            if (count === null || count === undefined) {
                return {
                    fillColor: "#cccccc",
                    color: "white",
                    weight: 1,
                    fillOpacity: 0.3
                };
            }

            let fillColor;

            if (count < 250) {
                fillColor = "#eff3ff";
            } else if (count < 350) {
                fillColor = "#c6dbef";
            } else if (count < 450) {
                fillColor = "#9ecae1";
            } else if (count < 550) {
                fillColor = "#4292c6";
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

    }
});