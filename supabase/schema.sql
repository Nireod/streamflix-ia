-- ============================================================================
--  Esquema de base de datos de StreamFlix para Supabase
--  Pega este script completo en:  Supabase → SQL Editor → New query → Run
-- ============================================================================
--  Crea dos tablas:
--    profiles  -> perfiles de visualización (tipo Netflix) por cuenta
--    movies    -> películas añadidas desde el formulario (catálogo compartido)
--  La autenticación (cuentas/login) la maneja Supabase Auth automáticamente
--  en el esquema auth; aquí solo guardamos los datos de la aplicación.
-- ============================================================================


-- ----------------------------------------------------------------------------
-- 1) PERFILES (varios por cuenta, como los perfiles de Netflix)
-- ----------------------------------------------------------------------------
create table if not exists public.profiles (
    id          uuid primary key default gen_random_uuid(),
    user_id     uuid not null references auth.users (id) on delete cascade,
    nombre      text not null,
    -- Arquetipo de gustos: alimenta el motor de recomendación.
    -- Valores sugeridos: 'Fan del terror clásico', 'Amante de la comedia',
    -- 'Cinéfilo de cine negro', 'Aficionado al cine mudo',
    -- 'Fan de ciencia ficción', 'Espectador generalista'.
    arquetipo   text not null default 'Espectador generalista',
    avatar      text default '🎬',
    created_at  timestamptz not null default now()
);

alter table public.profiles enable row level security;

-- Cada usuario solo puede ver y gestionar SUS propios perfiles.
drop policy if exists "perfiles propios - select" on public.profiles;
create policy "perfiles propios - select" on public.profiles
    for select using (auth.uid() = user_id);

drop policy if exists "perfiles propios - insert" on public.profiles;
create policy "perfiles propios - insert" on public.profiles
    for insert with check (auth.uid() = user_id);

drop policy if exists "perfiles propios - update" on public.profiles;
create policy "perfiles propios - update" on public.profiles
    for update using (auth.uid() = user_id);

drop policy if exists "perfiles propios - delete" on public.profiles;
create policy "perfiles propios - delete" on public.profiles
    for delete using (auth.uid() = user_id);


-- ----------------------------------------------------------------------------
-- 2) PELÍCULAS AÑADIDAS (catálogo compartido: las ve todo el mundo)
-- ----------------------------------------------------------------------------
create table if not exists public.movies (
    id           bigint generated always as identity primary key,
    titulo       text not null,
    anio         int,
    director     text,
    genero       text not null default 'Otro',
    sinopsis     text default '',
    poster       text default '',
    -- URL de reproducción. Puede ser:
    --   - un .mp4 directo  (o enlace de Google Drive /preview)
    --   - un embed de YouTube / Vimeo / Doodstream / archive.org
    embed_url    text not null,
    -- Características para el motor de recomendación (booleanos).
    accion       boolean default false,
    comedia      boolean default false,
    terror       boolean default false,
    drama        boolean default false,
    ciencia_ficcion boolean default false,
    romance      boolean default false,
    suspenso     boolean default false,
    cine_negro   boolean default false,
    aventura     boolean default false,
    mudo         boolean default false,
    clasico_pre1940 boolean default false,
    created_by   uuid references auth.users (id) on delete set null,
    created_at   timestamptz not null default now()
);

alter table public.movies enable row level security;

-- Cualquiera (incluso sin login) puede VER el catálogo compartido.
drop policy if exists "peliculas - lectura publica" on public.movies;
create policy "peliculas - lectura publica" on public.movies
    for select using (true);

-- Solo usuarios autenticados pueden AÑADIR películas.
drop policy if exists "peliculas - insertar autenticados" on public.movies;
create policy "peliculas - insertar autenticados" on public.movies
    for insert with check (auth.uid() is not null);

-- Cada quien puede borrar/editar las películas que él añadió.
drop policy if exists "peliculas - editar propias" on public.movies;
create policy "peliculas - editar propias" on public.movies
    for update using (auth.uid() = created_by);

drop policy if exists "peliculas - borrar propias" on public.movies;
create policy "peliculas - borrar propias" on public.movies
    for delete using (auth.uid() = created_by);


-- ============================================================================
--  Listo. Después de ejecutar:
--   - Ve a Authentication → Providers y confirma que "Email" está habilitado.
--   - (Opcional) Para "Entrar con Google", habilita el proveedor Google ahí.
-- ============================================================================
