/* ===== Formulario para añadir películas (guarda en Supabase) ===== */
import { getSupabase } from "/supabase-client.js";

const $ = (s) => document.querySelector(s);

const CARACTERISTICAS = [
  ["accion", "Acción"], ["comedia", "Comedia"], ["terror", "Terror"],
  ["drama", "Drama"], ["ciencia_ficcion", "Ciencia ficción"], ["romance", "Romance"],
  ["suspenso", "Suspenso"], ["cine_negro", "Cine negro"], ["aventura", "Aventura"],
  ["mudo", "Mudo"], ["clasico_pre1940", "Clásico (pre-1940)"],
];

let sb = null;
let usuario = null;

function pintarCheckboxes() {
  $("#caracts").innerHTML = CARACTERISTICAS.map(([k, label]) =>
    `<label class="check"><input type="checkbox" id="c_${k}" /> ${label}</label>`
  ).join("");
}

async function init() {
  pintarCheckboxes();
  sb = await getSupabase();

  if (!sb) {
    // Modo demo sin Supabase: no se puede persistir.
    $("#aviso-login").textContent =
      "Supabase no está configurado, así que no se pueden guardar películas (modo demo).";
    $("#aviso-login").classList.remove("oculto");
    $("#form-agregar").classList.add("oculto");
    return;
  }

  const { data: { session } } = await sb.auth.getSession();
  if (!session) {
    $("#aviso-login").classList.remove("oculto");
    $("#form-agregar").classList.add("oculto");
    return;
  }
  usuario = session.user;

  $("#form-agregar").addEventListener("submit", guardar);
}

async function guardar(e) {
  e.preventDefault();
  $("#error").classList.add("oculto");
  $("#ok").classList.add("oculto");
  $("#btn-guardar").disabled = true;

  const fila = {
    titulo: $("#titulo").value.trim(),
    anio: $("#anio").value ? Number($("#anio").value) : null,
    director: $("#director").value.trim(),
    genero: $("#genero").value,
    sinopsis: $("#sinopsis").value.trim(),
    poster: $("#poster").value.trim(),
    embed_url: $("#embed_url").value.trim(),
    created_by: usuario.id,
  };
  CARACTERISTICAS.forEach(([k]) => { fila[k] = $(`#c_${k}`).checked; });

  const { data, error } = await sb.from("movies").insert(fila).select().single();
  $("#btn-guardar").disabled = false;

  if (error) {
    $("#error").textContent = "No se pudo guardar: " + error.message;
    $("#error").classList.remove("oculto");
    return;
  }

  $("#ok").innerHTML =
    `✅ "${data.titulo}" añadida. ` +
    `<a href="/ver/sb_${data.id}">Reproducir ahora →</a> · <a href="/">Ver en el catálogo</a>`;
  $("#ok").classList.remove("oculto");
  $("#form-agregar").reset();
  pintarCheckboxes();
}

init();
