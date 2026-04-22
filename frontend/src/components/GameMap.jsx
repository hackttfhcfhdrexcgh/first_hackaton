// filepath: frontend/src/components/GameMap.jsx
import { useMemo, useState } from "react";
import Map, { Source, Layer, Popup } from "react-map-gl/maplibre";
import "maplibre-gl/dist/maplibre-gl.css";

const MINSK_CENTER = { longitude: 27.5615, latitude: 53.9045 };
const INITIAL_ZOOM = 12;
const MAP_STYLE = "https://tiles.openfreemap.org/styles/liberty";

function hexToGeoJSON(hexes) {
  return {
    type: "FeatureCollection",
    features: hexes.map((h) => ({
      type: "Feature",
      properties: {
        hex_id: h.hex_id,
        is_unlocked: !!h.is_unlocked,
        partner_name: h.partner?.name ?? null,
        partner_category: h.partner?.category ?? null,
        cashback: h.partner?.cashback_percent ?? null,
      },
      geometry: {
        type: "Polygon",
        coordinates: [h.vertices.map((v) => [v[1], v[0]]).concat([[h.vertices[0][1], h.vertices[0][0]]])],
      },
    })),
  };
}

export default function GameMap({ hexes }) {
  const [popup, setPopup] = useState(null);
  const hexGeoJSON = useMemo(() => hexToGeoJSON(hexes), [hexes]);

  return (
    <Map
      initialViewState={{
        longitude: MINSK_CENTER.longitude,
        latitude: MINSK_CENTER.latitude,
        zoom: INITIAL_ZOOM,
      }}
      mapStyle={MAP_STYLE}
      style={{ width: "100%", height: "100%" }}
      interactiveLayerIds={["hex-fill"]}
      onClick={(e) => {
        const f = e.features?.[0];
        if (f?.properties?.is_unlocked && f.properties.partner_name) {
          setPopup({
            lngLat: e.lngLat,
            name: f.properties.partner_name,
            category: f.properties.partner_category,
            cashback: f.properties.cashback,
          });
        } else {
          setPopup(null);
        }
      }}
    >
      <Source id="hexes" type="geojson" data={hexGeoJSON}>
        <Layer
          id="hex-fill"
          type="fill"
          paint={{
            "fill-color": "#6b6f78",
            "fill-opacity": [
              "case",
              ["boolean", ["get", "is_unlocked"], false],
              0.0,
              0.72,
            ],
          }}
        />
        <Layer
          id="hex-outline"
          type="line"
          paint={{
            "line-color": "#3a3d45",
            "line-width": 0.6,
            "line-opacity": [
              "case",
              ["boolean", ["get", "is_unlocked"], false],
              0.0,
              0.5,
            ],
          }}
        />
      </Source>

      {popup && (
        <Popup
          longitude={popup.lngLat.lng}
          latitude={popup.lngLat.lat}
          anchor="bottom"
          onClose={() => setPopup(null)}
          closeOnClick={false}
        >
          <div style={{ fontWeight: 600, marginBottom: 4 }}>{popup.name}</div>
          <div style={{ fontSize: 12 }}>Кэшбэк: {popup.cashback}%</div>
          <div style={{ fontSize: 11, color: "#666", marginTop: 2 }}>
            Категория: {popup.category}
          </div>
        </Popup>
      )}
    </Map>
  );
}
