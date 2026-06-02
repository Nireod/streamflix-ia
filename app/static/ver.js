/* ===== Página de reproducción /ver/{id} ===== */
import { getSupabase, filaAMovie } from "/supabase-client.js";

const id = window.PELICULA_ID;

function pintarReproductor(tipo, src) {
  const cont = document.getElementById("reproductor");
  if (!src) { cont.innerHTML = '<div class="cargando">Fuente de video no disponible.</div>'; return; }
  if (tipo === "video") {
    cont.innerHTML = `<video src="${src}" controls autoplay playsinline></video>`;
  } else {
    cont.innerHTML = `<iframe src="${src}" allowfullscreen frameborder="0" allow="autoplay; fullscreen"></iframe>`;
  }
}

function pintarInfo(peli, fuenteTexto) {
  document.getElementById("ver-titulo").textContent = peli.titulo;
  document.title = `${peli.titulo} — CineClásico`;
  const meta = [peli.anio, peli.genero, peli.director ? "Dir. " + peli.director : ""]
    .filter(Boolean).join(" · ");
  document.getElementById("ver-meta").textContent = meta;
  document.getElementById("ver-sinopsis").textContent = peli.sinopsis || "";
  document.getElementById("ver-fuente").innerHTML = fuenteTexto;
}

function pintarRelacionadas(lista) {
  if (!lista || !lista.length) return;
  const cont = document.getElementById("relacionadas");
  cont.innerHTML = lista.map((r) => `
    <a class="tarjeta" href="/ver/${r.id}">
      <img src="${r.poster}" alt="${r.titulo}" onerror="this.style.background='#2a2a2a';" />
      <div class="tarjeta-info">
        <div class="tarjeta-titulo">${r.titulo}</div>
        <div class="tarjeta-meta">${r.anio || ""} · ${r.genero}</div>
      </div>
    </a>`).join("");
  document.getElementById("fila-relacionadas").style.display = "";
}

async function cargar() {
  if (String(id).startsWith("sb_")) {
    // --- Película añadida en Supabase ---
    const sb = await getSupabase();
    if (!sb) { pintarReproductor("iframe", ""); return; }
    const realId = String(id).slice(3);
    const { data } = await sb.from("movies").select("*").eq("id", realId).single();
    if (!data) { document.getElementById("ver-titulo").textContent = "Película no encontrada"; return; }
    const peli = filaAMovie(data);
    // Normaliza el embed con el backend (detecta YouTube/MP4/Drive/etc.)
    const fuente = await (await fetch("/api/normalizar-embed?url=" + encodeURIComponent(peli.embed_url))).json();
    pintarReproductor(fuente.tipo, fuente.src);
    pintarInfo(peli, "🎬 Fuente añadida por el usuario.");
  } else {
    // --- Película del catálogo base ---
    const peli = await (await fetch("/api/pelicula/" + id)).json();
    if (peli.detail) { document.getElementById("ver-titulo").textContent = "Película no encontrada"; return; }
    pintarReproductor(peli.embed_tipo, peli.embed);
    const ident = (peli.embed.split("/").pop()) || "";
    pintarInfo(peli,
      `🎬 Película de dominio público alojada en ` +
      `<a href="https://archive.org/details/${ident}" target="_blank" rel="noopener">Internet Archive</a>.`);
    const rel = await (await fetch("/api/relacionadas/" + id + "?n=6")).json();
    if (Array.isArray(rel)) pintarRelacionadas(rel);
  }
}

cargar();
