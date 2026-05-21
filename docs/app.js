const GEOJSON_PATH = "data/kreise.geojson";
const LEGACY_GEOJSON_PATH = "data/kreise.geojson.json";
const METRICS_PATH = "data/metrics.json";

const map = L.map("map", {
  zoomControl: true,
  minZoom: 5,
  maxZoom: 11,
  maxBounds: [
    [45.0, 3.0],
    [56.5, 17.5],
  ],
  maxBoundsViscosity: 0.7,
}).setView([51.2, 10.4], 6);

L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
  maxZoom: 19,
  attribution:
    '&copy; OpenStreetMap-Mitwirkende &copy; <a href="https://carto.com/attributions">CARTO</a>',
}).addTo(map);

const infoBox = document.getElementById("infoBox");
const sourceBox = document.getElementById("sourceBox");
const statusMessage = document.getElementById("statusMessage");
const primaryMetricSelect = document.getElementById("primaryMetric");
const secondaryMetricSelect = document.getElementById("secondaryMetric");

let geojsonLayer = null;
let metricDefinitions = [];

function repairMojibake(value) {
  if (typeof value !== "string" || !/[ÃƒÃ‚]/.test(value)) {
    return value;
  }

  try {
    return decodeURIComponent(escape(value));
  } catch (_error) {
    return value;
  }
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (character) => {
    const replacements = {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#39;",
    };

    return replacements[character];
  });
}

function getRegionName(feature) {
  const props = feature.properties || {};
  return repairMojibake(
    props.GEN || props.NAME_3 || props.NAME || props.name || "Unbekannter Kreis"
  );
}

function getSeed(feature, metricId) {
  const props = feature.properties || {};
  const rawId = Number(props.ID_3 ?? feature.id ?? 1);
  const metricSalt = Array.from(metricId).reduce(
    (sum, character) => sum + character.charCodeAt(0),
    0
  );

  return (rawId * 1103515245 + metricSalt * 12345) >>> 0;
}

function createMvpValue(feature, metric) {
  const [min, max] = metric.range;
  const seed = getSeed(feature, metric.id);
  const fraction = (seed % 1000) / 999;
  const value = min + (max - min) * fraction;

  return metric.unit.includes("Euro") ? Math.round(value) : Number(value.toFixed(1));
}

function formatValue(value, metric) {
  if (metric.unit.includes("Euro")) {
    return new Intl.NumberFormat("de-DE").format(value);
  }

  return new Intl.NumberFormat("de-DE", {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  }).format(value);
}

function normalizeValue(value, metric) {
  const [min, max] = metric.range;

  if (max === min) {
    return 0;
  }

  return Math.max(0, Math.min(1, (value - min) / (max - min)));
}

function createCorrelationScore(feature, primary, secondary) {
  const primaryValue = createMvpValue(feature, primary);
  const secondaryValue = createMvpValue(feature, secondary);
  const primaryNorm = normalizeValue(primaryValue, primary);
  const secondaryNorm = normalizeValue(secondaryValue, secondary);
  const score = primaryNorm * secondaryNorm * 100;

  return {
    primaryValue,
    secondaryValue,
    primaryNorm,
    secondaryNorm,
    score,
  };
}

function formatScore(score) {
  return new Intl.NumberFormat("de-DE", {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(score);
}

function getSelectedMetrics() {
  const primary =
    metricDefinitions.find((metric) => metric.id === primaryMetricSelect.value) ||
    metricDefinitions[0];
  const secondary =
    metricDefinitions.find((metric) => metric.id === secondaryMetricSelect.value) ||
    metricDefinitions[1] ||
    metricDefinitions[0];

  return { primary, secondary };
}

function getFeatureStyle(feature) {
  const { primary, secondary } = getSelectedMetrics();
  const { score } = createCorrelationScore(feature, primary, secondary);
  const intensity = score / 100;
  const fill =
    intensity > 0.78
      ? "#2f594b"
      : intensity > 0.55
        ? "#5f8275"
        : intensity > 0.32
          ? "#9aaca4"
          : "#d8ddd9";

  return {
    weight: 0.8,
    color: "#727a74",
    opacity: 0.9,
    fillColor: fill,
    fillOpacity: 0.78,
  };
}

function getCorrelationTier(score) {
  if (score >= 67) {
    return {
      label: "alarmierend korrelatorisch",
      text:
        "Die Werte stehen so demonstrativ nebeneinander, dass der Korrelator kurz einen Laborkittel anziehen wollte. Wissenschaftlich bleibt das Quatsch.",
    };
  }

  if (score >= 34) {
    return {
      label: "verdaechtig mittel",
      text:
        "Fuer eine Stammtischthese reicht es schon fast. Fuer Forschung eher nicht, aber der Kreis schaut auffaellig unauffaellig aus.",
    };
  }

  return {
    label: "kaum gemeinsamer Ausschlag",
    text:
      "Die These muss noch im Keller reifen. Diese beiden Werte nicken sich hier hoechstens aus der Ferne zu.",
  };
}

function createSillyExplanation(regionName, primary, secondary, score) {
  const tier = getCorrelationTier(score);
  const templates = [
    `In ${regionName} treffen ${primary.label} und ${secondary.label} aufeinander. Die Einstufung lautet: ${tier.label}. Das beweist natuerlich gar nichts, ausser dass der Korrelator bedeutungsvoll in seine Kaffeetasse starrt.`,
    `${regionName} liefert eine Zahlensuppe, in der ${primary.label} und ${secondary.label} gemeinsam oben schwimmen. Das beweist nichts, klingt aber fuer drei Sekunden sehr ueberzeugend.`,
    `Wenn man beide Augen zudrueckt, erklaert ${secondary.label} hier bestimmt ${primary.label}. Wenn man eines wieder oeffnet, bleibt immerhin ein huebscher Score.`,
    `Der Kreis ${regionName} behauptet statistisch rein gar nichts. Der Korrelator behauptet trotzdem: Das Muster riecht nach Zufall mit Selbstbewusstsein.`,
  ];
  const index = Math.min(
    templates.length - 1,
    Math.floor((score / 100) * templates.length)
  );

  return {
    tier,
    text: templates[index],
  };
}

function renderInfo(feature) {
  const regionName = getRegionName(feature);
  const name = escapeHtml(regionName);
  const { primary, secondary } = getSelectedMetrics();
  const { primaryValue, secondaryValue, primaryNorm, secondaryNorm, score } =
    createCorrelationScore(feature, primary, secondary);
  const explanation = createSillyExplanation(regionName, primary, secondary, score);

  infoBox.innerHTML = `
    <p class="eyebrow">Korrelator-Score</p>
    <h1>${name}</h1>
    <p>Min-max-normalisierte Gleichzeitigkeit beider Kennzahlen. Keine echte Korrelation, keine Kausalitaet.</p>
    <div class="score-box">
      <strong>${formatScore(score)}%</strong>
      <span>${escapeHtml(explanation.tier.label)}</span>
    </div>
    <div class="metric-grid">
      <div class="metric">
        <span>${escapeHtml(primary.label)}</span>
        <strong>${formatValue(primaryValue, primary)}</strong>
        <span>${escapeHtml(primary.unit)} · normiert ${formatScore(primaryNorm * 100)}%</span>
      </div>
      <div class="metric">
        <span>${escapeHtml(secondary.label)}</span>
        <strong>${formatValue(secondaryValue, secondary)}</strong>
        <span>${escapeHtml(secondary.unit)} · normiert ${formatScore(secondaryNorm * 100)}%</span>
      </div>
    </div>
    <p class="silly-proof">${escapeHtml(explanation.text)}</p>
    <p class="hint">Hinweis: Das ist ein spielerischer Score aus Platzhalterwerten, kein Statistikbefund.</p>
  `;
}

function renderSources() {
  const { primary, secondary } = getSelectedMetrics();
  const selected = [primary, secondary].filter(Boolean);

  sourceBox.innerHTML = `
    <p class="eyebrow">Quellencheck</p>
    <h2>Oeffentlich greifbar</h2>
    <ul class="source-list">
      ${selected
        .map((metric) => {
          const statusClass = metric.sourceStatus === "public-ready" ? "" : "needs-work";
          const statusText =
            metric.sourceStatus === "public-ready"
              ? "direkt importierbar"
              : "oeffentlich, Import bauen";

          return `
            <li class="source-card">
              <a href="${escapeHtml(metric.sourceUrl)}" target="_blank" rel="noreferrer">#${metric.issue} ${escapeHtml(metric.label)}</a>
              <p>${escapeHtml(metric.sourceName)} · ${escapeHtml(metric.granularity)}</p>
              <p>${escapeHtml(metric.importNote)}</p>
              <span class="status-pill ${statusClass}">${statusText}</span>
            </li>
          `;
        })
        .join("")}
    </ul>
  `;
}

function showInitialInfo() {
  infoBox.innerHTML = `
    <p class="eyebrow">MVP</p>
    <h1>Korrelator 3000</h1>
    <p>Oeffentliche Quellen sind hinterlegt, Kartenwerte bleiben bis zum Import Platzhalter.</p>
  `;
}

function highlightFeature(event) {
  const layer = event.target;
  layer.setStyle({
    weight: 2,
    color: "#1f2328",
    fillOpacity: 0.92,
  });
  layer.bringToFront();
  renderInfo(layer.feature);
}

function resetHighlight(event) {
  if (geojsonLayer) {
    geojsonLayer.resetStyle(event.target);
  }
}

function zoomToFeature(event) {
  map.fitBounds(event.target.getBounds(), { padding: [28, 28], maxZoom: 8 });
  renderInfo(event.target.feature);
}

function bindFeature(feature, layer) {
  const name = getRegionName(feature);
  const { primary, secondary } = getSelectedMetrics();
  const { primaryValue, secondaryValue, score } = createCorrelationScore(
    feature,
    primary,
    secondary
  );

  layer.bindTooltip(
    `${name}: Score ${formatScore(score)}% · ${primary.label} ${formatValue(primaryValue, primary)} / ${secondary.label} ${formatValue(secondaryValue, secondary)}`,
    {
      sticky: true,
      direction: "top",
    }
  );

  layer.on({
    mouseover: highlightFeature,
    mouseout: resetHighlight,
    click: zoomToFeature,
  });
}

function refreshMap() {
  if (geojsonLayer) {
    geojsonLayer.setStyle(getFeatureStyle);
    geojsonLayer.eachLayer((layer) => {
      layer.unbindTooltip();
      bindFeature(layer.feature, layer);
    });
  }

  renderSources();
  showInitialInfo();
}

function populateMetricSelects() {
  metricDefinitions.forEach((metric) => {
    const displayLabel = metric.label
      .replace("Durchschnittseinkommen pro Kopf", "Einkommen pro Kopf")
      .replace(" Bundestagswahl 2025", " BTW 2025");
    const primaryOption = new Option(`#${metric.issue} ${displayLabel}`, metric.id);
    const secondaryOption = new Option(`#${metric.issue} ${displayLabel}`, metric.id);
    primaryMetricSelect.add(primaryOption);
    secondaryMetricSelect.add(secondaryOption);
  });

  primaryMetricSelect.value = "einkommen";
  secondaryMetricSelect.value = "schwimmbaeder";
  primaryMetricSelect.addEventListener("change", refreshMap);
  secondaryMetricSelect.addEventListener("change", refreshMap);
}

async function fetchJson(path) {
  const response = await fetch(path);

  if (!response.ok) {
    throw new Error(`${path} konnte nicht geladen werden (${response.status}).`);
  }

  return response.json();
}

async function loadGeoJson() {
  try {
    return await fetchJson(GEOJSON_PATH);
  } catch (primaryError) {
    console.warn(primaryError);

    try {
      statusMessage.textContent = "Standardpfad fehlt, versuche alten GeoJSON-Dateinamen...";
      return await fetchJson(LEGACY_GEOJSON_PATH);
    } catch (legacyError) {
      console.warn(legacyError);
      throw primaryError;
    }
  }
}

async function init() {
  statusMessage.textContent = "Lade Kennzahlen und Kreise...";
  metricDefinitions = await fetchJson(METRICS_PATH);
  populateMetricSelects();

  const data = await loadGeoJson();
  geojsonLayer = L.geoJSON(data, {
    style: getFeatureStyle,
    onEachFeature: bindFeature,
  }).addTo(map);

  map.fitBounds(geojsonLayer.getBounds(), { padding: [16, 16] });
  statusMessage.textContent = `${data.features.length} Kreis-Geometrien geladen. Werte sind MVP-Platzhalter.`;
  renderSources();
  showInitialInfo();
}

init().catch((error) => {
  console.error(error);
  statusMessage.classList.add("is-error");
  statusMessage.textContent =
    window.location.protocol === "file:"
      ? "Daten konnten nicht geladen werden. Starte die Seite ueber einen lokalen Server, nicht per Doppelklick."
      : "Daten konnten nicht geladen werden. Pruefe docs/data/kreise.geojson und docs/data/metrics.json.";
  infoBox.innerHTML = `
    <p class="eyebrow">Fehler</p>
    <h1>Keine Daten geladen</h1>
    <p>Erwartet werden <code>${GEOJSON_PATH}</code> und <code>${METRICS_PATH}</code> relativ zu <code>docs/index.html</code>.</p>
  `;
});
