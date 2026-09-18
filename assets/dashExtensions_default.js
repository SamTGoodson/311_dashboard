window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(feature) {
                const count = feature.properties.count ?? 0;

                let fillColor;

                if (count <= 0) {
                    fillColor = "#f7fbff";
                } else if (count <= 10) {
                    fillColor = "#deebf7";
                } else if (count <= 25) {
                    fillColor = "#c6dbef";
                } else if (count <= 50) {
                    fillColor = "#9ecae1";
                } else if (count <= 100) {
                    fillColor = "#6baed6";
                } else if (count <= 200) {
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
            const count = feature.properties.count ?? 0;

            layer.bindPopup(
                "<b>Community Board:</b> " + board +
                "<br><b>Complaints:</b> " + count
            );
        }

    }
});