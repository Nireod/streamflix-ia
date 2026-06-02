/* ===== CineClásico — lógica del frontend ===== */
import { getSupabase, peliculasAnadidas } from "/supabase-client.js";
import { icono } from "/iconos.js";

const $ = (sel) => document.querySelector(sel);
let usuarioActual = null;
let catalogoCache = null;
let perfilActivo = null;     // perfil elegido (de Supabase, vía localStorage)
let añadidasCache = null;    // películas añadidas en Supabase
let todasLasPelis = [];      // catálogo plano para la búsqueda

// --- Utilidades ---
async function api(ruta) {
  const r = await fetch(ruta);
  if (!r.ok) throw new Error("Error " + r.status + " en " + ruta);
  return r.json();
}

function escapar(s) {
  return String(s ?? "").replace(/[&<>"]/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
}

function crearTarjeta(peli, opciones = {}) {
  const div = document.createElement("div");
  div.className = "tarjeta";
  div.tabIndex = 0;
  div.setAttribute("role", "button");
  div.setAttribute("aria-label", `Reproducir ${peli.titulo}`);
  const badge = opciones.badge
    ? `<span class="badge ${opciones.badgeClase || ""}">${opciones.badge}</span>`
    : "";
  div.innerHTML = `
    ${badge}
    <img src="${peli.poster}" alt="${escapar(peli.titulo)}" loading="lazy"
         onerror="this.style.visibility='hidden';" />
    <div class="tarjeta-overlay">
      <div class="ov-titulo">${escapar(peli.titulo)}</div>
      <div class="ov-meta">${peli.anio || ""} · ${escapar(peli.genero)}</div>
      <span class="ov-play">${icono("play")} Reproducir</span>
    </div>
    <div class="tarjeta-info">
      <div class="tarjeta-titulo">${escapar(peli.titulo)}</div>
      <div class="tarjeta-meta">${peli.anio || ""} · ${escapar(peli.genero)}</div>
    </div>`;
  const ir = () => reproducir(peli);
  div.addEventListener("click", ir);
  div.addEventListener("keydown", (e) => {
    if (e.key === "Enter" || e.key === " ") { e.preventDefault(); ir(); }
  });
  return div;
}

function crearFila(titulo, peliculas, opciones = {}) {
  const fila = document.createElement("section");
  fila.className = "fila";
  const h2 = document.createElement("h2");
  h2.className = "fila-titulo" + (opciones.destacada ? " destacada" : "");
  h2.innerHTML = (opciones.icono ? icono(opciones.icono) : "") + `<span>${escapar(titulo)}</span>`;
  fila.appendChild(h2);

  const wrap = document.createElement("div");
  wrap.className = "carrusel-wrap";

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

  // Flechas de navegación del carrusel
  const izq = document.createElement("button");
  izq.className = "flecha izq";
  izq.setAttribute("aria-label", "Anterior");
  izq.innerHTML = icono("chevron-left");
  izq.addEventListener("click", () => carrusel.scrollBy({ left: -600, behavior: "smooth" }));

  const der = document.createElement("button");
  der.className = "flecha der";
  der.setAttribute("aria-label", "Siguiente");
  der.innerHTML = icono("chevron-right");
  der.addEventListener("click", () => carrusel.scrollBy({ left: 600, behavior: "smooth" }));

  wrap.appendChild(izq);
  wrap.appendChild(carrusel);
  wrap.appendChild(der);
  fila.appendChild(wrap);
  return fila;
}

// Skeleton de carga (mientras llegan las recomendaciones).
function filaSkeleton() {
  const fila = document.createElement("section");
  fila.className = "fila";
  fila.innerHTML = `<h2 class="fila-titulo"><span class="skeleton" style="height:20px;width:200px;display:block;border-radius:4px"></span></h2>`;
  const wrap = document.createElement("div");
  wrap.className = "carrusel-wrap";
  const car = document.createElement("div");
  car.className = "carrusel";
  for (let i = 0; i < 8; i++) {
    const sk = document.createElement("div");
    sk.className = "skeleton sk-card";
    car.appendChild(sk);
  }
  wrap.appendChild(car);
  fila.appendChild(wrap);
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
  $("#hero-play").innerHTML = icono("play") + " Reproducir";
  $("#hero-info").innerHTML = icono("info") + " Más información";
  $("#hero-play").onclick = () => reproducir(peli);
  $("#hero-info").onclick = () => reproducir(peli);
}

// --- Carga principal por usuario ---
async function cargarParaUsuario(uid) {
  usuarioActual = uid;
  const filas = $("#filas");

  // Mostrar skeletons mientras llega todo.
  filas.innerHTML = "";
  for (let i = 0; i < 3; i++) filas.appendChild(filaSkeleton());

  // Catálogo (una sola vez)
  if (!catalogoCache) catalogoCache = await api("/api/catalogo");

  // Recomendaciones personalizadas
  const recs = await api(`/api/recomendaciones/${uid}`);

  // Ya tenemos datos: limpiamos skeletons.
  filas.innerHTML = "";

  // Hero: la mejor recomendación colaborativa (o la primera del catálogo)
  const destacada = recs.colaborativo[0]
    ? recs.colaborativo[0].pelicula
    : catalogoCache.peliculas[0];
  pintarHero(destacada);

  // Fila 1: recomendado para ti (filtrado colaborativo)
  if (recs.colaborativo.length) {
    filas.appendChild(
      crearFila("Recomendado para ti", recs.colaborativo, { destacada: true, icono: "sparkles" })
    );
  }

  // Fila 2: porque coincide con tu perfil (árbol de decisión)
  if (recs.arbol.length) {
    filas.appendChild(
      crearFila("Según tu perfil (árbol de decisión)", recs.arbol, { icono: "git-branch" })
    );
  }

  // Fila: películas añadidas por usuarios (Supabase), si las hay.
  if (añadidasCache && añadidasCache.length) {
    filas.appendChild(crearFila("Añadidas a CineClásico", añadidasCache, { icono: "film" }));
  }

  // Filas por género (mezclando catálogo base + añadidas del mismo género)
  const porGenero = { ...catalogoCache.por_genero };
  (añadidasCache || []).forEach((p) => {
    (porGenero[p.genero] = porGenero[p.genero] || []).push(p);
  });
  Object.entries(porGenero).forEach(([genero, pelis]) => {
    filas.appendChild(crearFila(genero, pelis));
  });

  // Construir índice plano para la búsqueda.
  todasLasPelis = [...catalogoCache.peliculas, ...(añadidasCache || [])];

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

// Mapea el arquetipo del perfil activo al usuario del motor de recomendación.
function usuarioParaArquetipo(usuarios, arquetipo) {
  const match = usuarios.find((u) => u.arquetipo === arquetipo);
  return match ? match.id : usuarios[0].id;
}

// --- Init ---
async function init() {
  const usuarios = await api("/api/usuarios");

  // ¿Supabase activo y hay sesión? Si está activo pero sin sesión -> login.
  const sb = await getSupabase();
  if (sb) {
    const { data: { session } } = await sb.auth.getSession();
    if (!session) { window.location.href = "/login"; return; }
    // Perfil activo elegido en /perfiles.
    const guardado = localStorage.getItem("streamflix_perfil");
    if (!guardado) { window.location.href = "/perfiles"; return; }
    perfilActivo = JSON.parse(guardado);
    // Cargar películas añadidas (catálogo compartido).
    añadidasCache = await peliculasAnadidas();
  }

  // Barra superior: nombre del perfil + acciones.
  pintarBarraPerfil(usuarios, sb);

  // Selector de perfil (modo demo) o usuario mapeado por arquetipo.
  const selector = $("#selector-perfil");
  usuarios.forEach((u) => {
    const opt = document.createElement("option");
    opt.value = u.id;
    opt.textContent = u.nombre;
    selector.appendChild(opt);
  });
  selector.addEventListener("change", (e) => cargarParaUsuario(Number(e.target.value)));

  const inicial = perfilActivo
    ? usuarioParaArquetipo(usuarios, perfilActivo.arquetipo)
    : usuarios[0].id;
  selector.value = inicial;
  await cargarParaUsuario(inicial);
  cargarMetricas();
}

function pintarBarraPerfil(usuarios, sb) {
  if (perfilActivo) {
    // Logueado: ocultar el selector demo y mostrar perfil + acciones.
    $("#demo-selector").style.display = "none";
    const acciones = document.createElement("div");
    acciones.className = "perfil-acciones";
    acciones.innerHTML = `
      <a class="btn btn-mini" href="/agregar">＋ Añadir película</a>
      <a class="btn btn-mini" href="/perfiles">${perfilActivo.avatar || "🎬"} ${perfilActivo.nombre}</a>
      <button class="btn btn-mini" id="btn-logout">Salir</button>`;
    $("#perfil-box").appendChild(acciones);
    $("#btn-logout").addEventListener("click", async () => {
      localStorage.removeItem("streamflix_perfil");
      if (sb) await sb.auth.signOut();
      window.location.href = "/login";
    });
  }
  // En modo demo (sin Supabase) se mantiene el selector de perfil ya presente.
}

init();
