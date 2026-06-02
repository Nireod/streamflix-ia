/* ===== Login / Registro con Supabase Auth ===== */
import { getSupabase, obtenerConfig } from "/supabase-client.js";

let modo = "login"; // "login" | "registro"

const $ = (s) => document.querySelector(s);

function mostrarError(msg) {
  const e = $("#auth-error");
  e.textContent = msg;
  e.classList.remove("oculto");
}

function cambiarModo(nuevo) {
  modo = nuevo;
  const esLogin = modo === "login";
  $("#auth-titulo").textContent = esLogin ? "Iniciar sesión" : "Crear cuenta";
  $("#btn-enviar").textContent = esLogin ? "Entrar" : "Registrarme";
  $("#switch-texto").textContent = esLogin ? "¿No tienes cuenta?" : "¿Ya tienes cuenta?";
  $("#switch-link").textContent = esLogin ? "Regístrate" : "Inicia sesión";
  $("#auth-error").classList.add("oculto");
}

async function init() {
  const cfg = await obtenerConfig();

  // Si Supabase no está configurado, mostramos el aviso de modo demo.
  if (!cfg.auth_habilitado) {
    $("#aviso-demo").classList.remove("oculto");
    $("#form-auth").classList.add("oculto");
    $(".auth-switch").classList.add("oculto");
    return;
  }

  const sb = await getSupabase();

  // Si ya hay sesión, saltar directo a la selección de perfil.
  const { data: { session } } = await sb.auth.getSession();
  if (session) { window.location.href = "/perfiles"; return; }

  $("#switch-link").addEventListener("click", (e) => {
    e.preventDefault();
    cambiarModo(modo === "login" ? "registro" : "login");
  });

  $("#form-auth").addEventListener("submit", async (e) => {
    e.preventDefault();
    $("#auth-error").classList.add("oculto");
    const email = $("#email").value.trim();
    const password = $("#password").value;
    $("#btn-enviar").disabled = true;

    let resultado;
    if (modo === "login") {
      resultado = await sb.auth.signInWithPassword({ email, password });
    } else {
      resultado = await sb.auth.signUp({ email, password });
    }
    $("#btn-enviar").disabled = false;

    if (resultado.error) {
      mostrarError(resultado.error.message);
      return;
    }
    if (modo === "registro" && !resultado.data.session) {
      mostrarError("Cuenta creada. Revisa tu correo para confirmar, o inicia sesión si la confirmación está desactivada.");
      cambiarModo("login");
      return;
    }
    window.location.href = "/perfiles";
  });
}

init();
