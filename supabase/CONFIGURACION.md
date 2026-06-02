# Configurar Supabase para StreamFlix

La app funciona **sin Supabase** (modo demo, con los perfiles ficticios). Para
activar el **login real**, los **perfiles por cuenta** y poder **añadir películas
que se guarden**, sigue estos pasos.

## 1. Crear el proyecto

1. Entra a <https://supabase.com> y crea un proyecto (plan gratuito).
2. Elige una contraseña para la base de datos y espera a que se aprovisione.

## 2. Crear las tablas

1. En el panel de Supabase ve a **SQL Editor → New query**.
2. Abre el archivo [`schema.sql`](schema.sql) de este repo, copia **todo** su
   contenido, pégalo y pulsa **Run**.
3. Deberías ver "Success". Esto crea las tablas `profiles` y `movies` con sus
   políticas de seguridad (RLS).

## 3. Confirmar el proveedor de Email

1. Ve a **Authentication → Providers**.
2. Asegúrate de que **Email** está habilitado.
3. (Opcional, recomendado para la demo) En **Authentication → Providers → Email**,
   desactiva *"Confirm email"* para poder entrar sin tener que confirmar el correo.

## 4. Copiar las claves públicas

1. Ve a **Project Settings → API**.
2. Copia dos valores:
   - **Project URL** → `https://xxxxxxxx.supabase.co`
   - **anon public** key → `eyJ...` (es larga)

> Estas dos claves son **públicas por diseño**; la seguridad la dan las políticas
> RLS. **No** uses la `service_role` key en el frontend.

## 5. Conectarlas a la app

### En local (para probar en tu PC)

Define las variables de entorno antes de arrancar el servidor:

**Windows (PowerShell):**
```powershell
$env:SUPABASE_URL = "https://xxxxxxxx.supabase.co"
$env:SUPABASE_ANON_KEY = "eyJ..."
uvicorn app.main:app --reload
```

### En Render (producción)

1. En tu servicio de Render ve a **Environment → Environment Variables**.
2. Añade dos variables:
   - `SUPABASE_URL` = tu Project URL
   - `SUPABASE_ANON_KEY` = tu anon public key
3. Guarda. Render redesplegará y el login quedará activo.

## 6. (Opcional) Entrar con Google

1. En **Google Cloud Console** crea un *OAuth Client ID* (tipo "Web application").
2. En *Authorized redirect URIs* añade la URL que te indica Supabase
   (**Authentication → Providers → Google** muestra la *callback URL*).
3. Copia el **Client ID** y **Client Secret** en Supabase → Google → y actívalo.
4. El botón "Continuar con Google" del login empezará a funcionar.

---

Una vez configurado:
- `/login` permite registrarse e iniciar sesión.
- `/perfiles` permite crear varios perfiles por cuenta (tipo Netflix).
- `/agregar` permite añadir películas con cualquier enlace de video.
