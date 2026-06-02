/* ===== Cliente Supabase compartido =====
   Inicializa supabase-js con la config pública que sirve el backend (/api/config).
   Si Supabase no está configurado (sin variables de entorno), exporta null y la
   app funciona en "modo demo" sin login. */

import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

let _cliente = null;
let _config = null;

export async function obtenerConfig() {
  if (_config) return _config;
  const r = await fetch("/api/config");
  _config = await r.json();
  return _config;
}

export async function getSupabase() {
  if (_cliente) return _cliente;
  const cfg = await obtenerConfig();
  if (!cfg.auth_habilitado) return null; // modo demo sin Supabase
  _cliente = createClient(cfg.supabase_url, cfg.supabase_anon_key);
  return _cliente;
}

/** Devuelve la sesión actual (o null si no hay login). */
export async function sesionActual() {
  const sb = await getSupabase();
  if (!sb) return null;
  const { data } = await sb.auth.getSession();
  return data.session;
}

/** Mapea una fila de la tabla 'movies' de Supabase al formato del frontend. */
export function filaAMovie(row) {
  return {
    id: "sb_" + row.id,
    titulo: row.titulo,
    anio: row.anio,
    director: row.director || "",
    genero: row.genero || "Otro",
    sinopsis: row.sinopsis || "",
    poster: row.poster || "",
    embed_url: row.embed_url,
    caracteristicas: {
      accion: row.accion, comedia: row.comedia, terror: row.terror,
      drama: row.drama, ciencia_ficcion: row.ciencia_ficcion,
      romance: row.romance, suspenso: row.suspenso, cine_negro: row.cine_negro,
      aventura: row.aventura, mudo: row.mudo, clasico_pre1940: row.clasico_pre1940,
    },
  };
}

/** Trae las películas añadidas en Supabase (catálogo compartido). */
export async function peliculasAnadidas() {
  const sb = await getSupabase();
  if (!sb) return [];
  const { data, error } = await sb.from("movies").select("*").order("created_at", { ascending: false });
  if (error) { console.warn("No se pudieron leer películas de Supabase:", error.message); return []; }
  return (data || []).map(filaAMovie);
}
