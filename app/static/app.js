/* ===== StreamFlix — lógica del frontend ===== */

const $ = (sel) => document.querySelector(sel);
let usuarioActual = null;
let catalogoCache = null;

// --- Utilidades ---
async function api(ruta) {
  const r = await fetch(ruta);
  if (!r.ok) throw new Error("Error " + r.status + " en " + ruta);
  return r.json();
}

function crearTarjeta(peli, opciones = {}) {
  const div = document.createElement("div");
  div.className = "tarjeta";
  const badge = opciones.badge
    ? `<span class="badge ${opciones.badgeClase || ""}">${opciones.badge}</span>`
    : "";
  div.innerHTML = `
    ${badge}
    <img src="${peli.poster}" alt="${peli.titulo}"
         onerror="this.style.background='#2a2a2a';this.alt='Sin carátula';" />
    <div class="tarjeta-info">
      <div class="tarjeta-titulo">${peli.titulo}</div>
      <div class="tarjeta-meta">${peli.anio} · ${peli.genero}</div>
    </div>`;
  div.addEventListener("click", () => reproducir(peli));
  return div;
}

function crearFila(titulo, peliculas, opciones = {}) {
  const fila = document.createElement("section");
  fila.className = "fila";
  const h2 = document.createElement("h2");
  h2.className = "fila-titulo" + (opciones.destacada ? " destacada" : "");
  h2.textContent = titulo;
  fila.appendChild(h2);

  const carrusel = document.createElement("div");
  carrusel.className = "carrusel";
  peliculas.forEach((item) => {
    const peli = item.pelicula || item;
    const opc = {};
    if (item.rating_predicho !== undefined) {
      opc.badge = "★ " + item.rating_predicho;
      opc.badgeClase = "pred";
    }
    carrusel.appendChild(crearTarjeta(peli, opc));
  });
  fila.appendChild(carrusel);
  return fila;
}

// --- Reproducción: navega a la página propia /ver/{id} ---
function reproducir(peli) {
  window.location.href = `/ver/${peli.id}`;
}

// --- Hero ---
function pintarHero(peli) {
  const hero = $("#hero");
  hero.style.backgroundImage = `url('${peli.poster}')`;
  $("#hero-titulo").textContent = peli.titulo;
  $("#hero-sinopsis").textContent = peli.sinopsis;
  $("#hero-play").onclick = () => reproducir(peli);
  $("#hero-info").onclick = () => reproducir(peli);
}

// --- Carga principal por usuario ---
async function cargarParaUsuario(uid) {
  usuarioActual = uid;
  const filas = $("#filas");
  filas.innerHTML = "";

  // Catálogo (una sola vez)
  if (!catalogoCache) catalogoCache = await api("/api/catalogo");

  // Recomendaciones personalizadas
  const recs = await api(`/api/recomendaciones/${uid}`);

  // Hero: la mejor recomendación colaborativa (o la primera del catálogo)
  const destacada = recs.colaborativo[0]
    ? recs.colaborativo[0].pelicula
    : catalogoCache.peliculas[0];
  pintarHero(destacada);

  // Fila 1: recomendado para ti (filtrado colaborativo)
  if (recs.colaborativo.length) {
    filas.appendChild(
      crearFila("✨ Recomendado para ti", recs.colaborativo, { destacada: true })
    );
  }

  // Fila 2: porque coincide con tu perfil (árbol de decisión)
  if (recs.arbol.length) {
    filas.appendChild(
      crearFila("🌳 Según tu perfil (árbol de decisión)", recs.arbol)
    );
  }

  // Filas por género
  Object.entries(catalogoCache.por_genero).forEach(([genero, pelis]) => {
    filas.appendChild(crearFila(genero, pelis));
  });

  // Panel comparación + métricas
  cargarComparacion(uid);
}

// --- Panel de métricas y comparación ---
async function cargarMetricas() {
  try {
    const m = await api("/api/metricas");
    const grid = $("#metricas-grid");
    grid.innerHTML = `
      <div class="metrica-card">
        <div class="valor">${(m.arbol_decision.precision * 100).toFixed(1)}%</div>
        <div class="etiqueta">Precisión del árbol de decisión<br>(cross-validation k=${m.arbol_decision.k_folds})</div>
      </div>
      <div class="metrica-card">
        <div class="valor">${m.filtrado_colaborativo.rmse}</div>
        <div class="etiqueta">RMSE filtrado colaborativo<br>(escala 1–5)</div>
      </div>
      <div class="metrica-card">
        <div class="valor">${m.filtrado_colaborativo.mae}</div>
        <div class="etiqueta">MAE filtrado colaborativo<br>(error medio en estrellas)</div>
      </div>`;
  } catch (e) {
    $("#metricas-grid").innerHTML = "<p>No se pudieron cargar las métricas.</p>";
  }
}

async function cargarComparacion(uid) {
  try {
    const c = await api(`/api/comparacion/${uid}?n=5`);
    const cont = $("#comparacion");
    const actual = c.sistema_actual_popularidad
      .map((x) => `<li>${x.titulo}<small>⭐ ${x.rating_promedio} (promedio global)</small></li>`)
      .join("");
    const nuevo = c.sistema_nuevo_personalizado
      .map((x) => `<li>${x.titulo}<small>★ ${x.rating_predicho} · ${x.motivo}</small></li>`)
      .join("");
    cont.innerHTML = `
      <div class="col actual">
        <h3>Sistema ACTUAL (popularidad)</h3>
        <ul>${actual}</ul>
      </div>
      <div class="col nuevo">
        <h3>Sistema NUEVO (IA personalizada)</h3>
        <ul>${nuevo}</ul>
      </div>`;
  } catch (e) {
    $("#comparacion").innerHTML = "";
  }
}

// --- Navbar sólida al hacer scroll ---
window.addEventListener("scroll", () => {
  $("#navbar").classList.toggle("solido", window.scrollY > 60);
});

// --- Init ---
async function init() {
  const usuarios = await api("/api/usuarios");
  const selector = $("#selector-perfil");
  usuarios.forEach((u) => {
    const opt = document.createElement("option");
    opt.value = u.id;
    opt.textContent = u.nombre;
    selector.appendChild(opt);
  });
  selector.addEventListener("change", (e) => cargarParaUsuario(Number(e.target.value)));

  await cargarParaUsuario(usuarios[0].id);
  cargarMetricas();
}

init();
