/* ===== Selección y creación de perfiles (tipo Netflix) ===== */
import { getSupabase } from "/supabase-client.js";

const $ = (s) => document.querySelector(s);
const AVATARES = ["🎬", "🍿", "👻", "🤠", "🚀", "🕵️", "🎭", "❤️"];

let sb = null;
let usuario = null;

async function cargarPerfiles() {
  const { data } = await sb.from("profiles").select("*").order("created_at");
  const grid = $("#perfiles-grid");
  grid.innerHTML = "";

  (data || []).forEach((p) => {
    const div = document.createElement("div");
    div.className = "perfil-card";
    div.innerHTML = `<div class="perfil-avatar">${p.avatar || "🎬"}</div>
                     <div class="perfil-nombre">${p.nombre}</div>
                     <div class="perfil-arq">${p.arquetipo}</div>`;
    div.addEventListener("click", () => elegirPerfil(p));
    grid.appendChild(div);
  });

  // Tarjeta "añadir perfil"
  const add = document.createElement("div");
  add.className = "perfil-card perfil-add";
  add.innerHTML = `<div class="perfil-avatar">＋</div><div class="perfil-nombre">Agregar perfil</div>`;
  add.addEventListener("click", abrirModal);
  grid.appendChild(add);
}

function elegirPerfil(p) {
  // Guardamos el perfil activo para que la home lo use en las recomendaciones.
  localStorage.setItem("streamflix_perfil", JSON.stringify({
    id: p.id, nombre: p.nombre, arquetipo: p.arquetipo, avatar: p.avatar,
  }));
  window.location.href = "/";
}

async function abrirModal() {
  // Cargar arquetipos disponibles desde el backend.
  const arqs = await (await fetch("/api/arquetipos")).json();
  const sel = $("#perfil-arquetipo");
  sel.innerHTML = arqs.map((a) => `<option value="${a}">${a}</option>`).join("");
  $("#modal-perfil").classList.remove("oculto");
}

$("#cerrar-perfil").addEventListener("click", () => $("#modal-perfil").classList.add("oculto"));

$("#form-perfil").addEventListener("submit", async (e) => {
  e.preventDefault();
  const nombre = $("#perfil-nombre").value.trim();
  const arquetipo = $("#perfil-arquetipo").value;
  const avatar = AVATARES[Math.floor(Math.random() * AVATARES.length)];
  const { error } = await sb.from("profiles").insert({
    user_id: usuario.id, nombre, arquetipo, avatar,
  });
  if (error) { alert("No se pudo crear el perfil: " + error.message); return; }
  $("#modal-perfil").classList.add("oculto");
  $("#perfil-nombre").value = "";
  cargarPerfiles();
});

$("#btn-salir").addEventListener("click", async () => {
  await sb.auth.signOut();
  window.location.href = "/login";
});

async function init() {
  sb = await getSupabase();
  if (!sb) { window.location.href = "/"; return; } // modo demo: sin perfiles

  const { data: { session } } = await sb.auth.getSession();
  if (!session) { window.location.href = "/login"; return; }
  usuario = session.user;
  cargarPerfiles();
}

init();
