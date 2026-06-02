"""
Catálogo de películas de StreamFlix.

Todas las películas son de DOMINIO PÚBLICO y están alojadas en Internet Archive
(archive.org), por lo que pueden reproducirse legalmente embebiendo el reproductor
oficial: https://archive.org/embed/<archive_id>

Cada película incluye un vector de características binarias (0/1) que describe sus
atributos. Ese vector es el que consume tanto el filtrado basado en contenido como
el árbol de decisión.

Características (en orden):
    accion, comedia, terror, drama, ciencia_ficcion, romance,
    suspenso, cine_negro, mudo, clasico_pre1940
"""

# Nombres de las características en orden. Sirve para el árbol de decisión.
CARACTERISTICAS = [
    "accion",
    "comedia",
    "terror",
    "drama",
    "ciencia_ficcion",
    "romance",
    "suspenso",
    "cine_negro",
    "mudo",
    "clasico_pre1940",
]


def _features(**kwargs):
    """Construye el vector de características poniendo en 1 las indicadas."""
    return {c: (1 if kwargs.get(c) else 0) for c in CARACTERISTICAS}


# id interno -> datos. El campo archive_id es el identificador REAL en archive.org.
PELICULAS = [
    {
        "id": 1,
        "titulo": "Nosferatu",
        "anio": 1922,
        "director": "F. W. Murnau",
        "genero": "Terror",
        "archive_id": "Nosferatu1922",
        "poster": "https://archive.org/services/img/Nosferatu1922",
        "sinopsis": "El conde Orlok, un vampiro de Transilvania, siembra el terror "
                    "en una ciudad alemana. Obra maestra del cine expresionista.",
        "caracteristicas": _features(terror=1, suspenso=1, mudo=1, clasico_pre1940=1),
    },
    {
        "id": 2,
        "titulo": "El gabinete del Dr. Caligari",
        "anio": 1920,
        "director": "Robert Wiene",
        "genero": "Terror",
        "archive_id": "DasKabinettdesDoktorCaligariTheCabinetofDrCaligari",
        "poster": "https://archive.org/services/img/DasKabinettdesDoktorCaligariTheCabinetofDrCaligari",
        "sinopsis": "Un hipnotizador usa a un sonámbulo para cometer asesinatos. "
                    "Pieza fundamental del expresionismo alemán.",
        "caracteristicas": _features(terror=1, suspenso=1, mudo=1, clasico_pre1940=1),
    },
    {
        "id": 3,
        "titulo": "Metropolis",
        "anio": 1927,
        "director": "Fritz Lang",
        "genero": "Ciencia ficción",
        "archive_id": "Metropolis1927EnglishVersion",
        "poster": "https://archive.org/services/img/Metropolis1927EnglishVersion",
        "sinopsis": "En una ciudad futurista dividida en clases, un joven y una obrera "
                    "intentan reconciliar a trabajadores y dirigentes.",
        "caracteristicas": _features(ciencia_ficcion=1, drama=1, mudo=1, clasico_pre1940=1),
    },
    {
        "id": 4,
        "titulo": "La quimera del oro",
        "anio": 1925,
        "director": "Charles Chaplin",
        "genero": "Comedia",
        "archive_id": "the-gold-rush-film-1925",
        "poster": "https://archive.org/services/img/the-gold-rush-film-1925",
        "sinopsis": "Charlot busca fortuna en Alaska durante la fiebre del oro, "
                    "entre aventuras, hambre y amor.",
        "caracteristicas": _features(comedia=1, romance=1, mudo=1, clasico_pre1940=1),
    },
    {
        "id": 5,
        "titulo": "El maquinista de La General",
        "anio": 1926,
        "director": "Buster Keaton",
        "genero": "Comedia",
        "archive_id": "TheGeneral_201312",
        "poster": "https://archive.org/services/img/TheGeneral_201312",
        "sinopsis": "Un maquinista persigue a los soldados que robaron su locomotora "
                    "durante la Guerra Civil estadounidense.",
        "caracteristicas": _features(comedia=1, accion=1, mudo=1, clasico_pre1940=1),
    },
    {
        "id": 6,
        "titulo": "El moderno Sherlock Holmes",
        "anio": 1924,
        "director": "Buster Keaton",
        "genero": "Comedia",
        "archive_id": "MyMovie_20190318",
        "poster": "https://archive.org/services/img/MyMovie_20190318",
        "sinopsis": "Un proyeccionista que sueña con ser detective se mete literalmente "
                    "dentro de la película que proyecta.",
        "caracteristicas": _features(comedia=1, romance=1, mudo=1, clasico_pre1940=1),
    },
    {
        "id": 7,
        "titulo": "El acorazado Potemkin",
        "anio": 1925,
        "director": "Serguéi Eisenstein",
        "genero": "Drama",
        "archive_id": "BattleshipPotemkin",
        "poster": "https://archive.org/services/img/BattleshipPotemkin",
        "sinopsis": "La tripulación de un acorazado se amotina contra sus oficiales. "
                    "Célebre por la secuencia de la escalinata de Odesa.",
        "caracteristicas": _features(drama=1, accion=1, mudo=1, clasico_pre1940=1),
    },
    {
        "id": 8,
        "titulo": "El fantasma de la ópera",
        "anio": 1925,
        "director": "Rupert Julian",
        "genero": "Terror",
        "archive_id": "ThePhantomOfTheOpera1925NewYorkGeneralReleasePrint_620",
        "poster": "https://archive.org/services/img/ThePhantomOfTheOpera1925NewYorkGeneralReleasePrint_620",
        "sinopsis": "Un misterioso fantasma que habita la Ópera de París se obsesiona "
                    "con una joven cantante.",
        "caracteristicas": _features(terror=1, drama=1, romance=1, mudo=1, clasico_pre1940=1),
    },
    {
        "id": 9,
        "titulo": "La noche de los muertos vivientes",
        "anio": 1968,
        "director": "George A. Romero",
        "genero": "Terror",
        "archive_id": "night-of-the-living-dead-1968-english",
        "poster": "https://archive.org/services/img/night-of-the-living-dead-1968-english",
        "sinopsis": "Un grupo de personas se refugia en una granja mientras los muertos "
                    "regresan a la vida. Fundó el cine moderno de zombis.",
        "caracteristicas": _features(terror=1, suspenso=1),
    },
    {
        "id": 10,
        "titulo": "Carnival of Souls",
        "anio": 1962,
        "director": "Herk Harvey",
        "genero": "Terror",
        "archive_id": "CarnivalofSouls",
        "poster": "https://archive.org/services/img/CarnivalofSouls",
        "sinopsis": "Tras un accidente, una mujer se siente atraída por un pabellón "
                    "abandonado y perseguida por figuras espectrales.",
        "caracteristicas": _features(terror=1, suspenso=1, drama=1),
    },
    {
        "id": 11,
        "titulo": "House on Haunted Hill",
        "anio": 1959,
        "director": "William Castle",
        "genero": "Terror",
        "archive_id": "house_on_haunted_hill_ipod",
        "poster": "https://archive.org/services/img/house_on_haunted_hill_ipod",
        "sinopsis": "Un millonario excéntrico ofrece dinero a cinco invitados si "
                    "sobreviven una noche en una mansión embrujada.",
        "caracteristicas": _features(terror=1, suspenso=1),
    },
    {
        "id": 12,
        "titulo": "Plan 9 from Outer Space",
        "anio": 1959,
        "director": "Ed Wood",
        "genero": "Ciencia ficción",
        "archive_id": "774-plan-9-from-outer-space",
        "poster": "https://archive.org/services/img/774-plan-9-from-outer-space",
        "sinopsis": "Alienígenas resucitan a los muertos para frenar a la humanidad. "
                    "Célebre película de culto de serie B.",
        "caracteristicas": _features(ciencia_ficcion=1, terror=1),
    },
    {
        "id": 13,
        "titulo": "Detour",
        "anio": 1945,
        "director": "Edgar G. Ulmer",
        "genero": "Cine negro",
        "archive_id": "detour-1945",
        "poster": "https://archive.org/services/img/detour-1945",
        "sinopsis": "Un pianista que cruza el país haciendo autostop se ve atrapado "
                    "en una espiral de muerte y chantaje.",
        "caracteristicas": _features(cine_negro=1, drama=1, suspenso=1),
    },
    {
        "id": 14,
        "titulo": "Scarlet Street",
        "anio": 1945,
        "director": "Fritz Lang",
        "genero": "Cine negro",
        "archive_id": "ScarletStreet",
        "poster": "https://archive.org/services/img/ScarletStreet",
        "sinopsis": "Un cajero de mediana edad se obsesiona con una mujer que lo "
                    "manipula a él y a su pintura.",
        "caracteristicas": _features(cine_negro=1, drama=1, romance=1, suspenso=1),
    },
    {
        "id": 15,
        "titulo": "His Girl Friday",
        "anio": 1940,
        "director": "Howard Hawks",
        "genero": "Comedia",
        "archive_id": "HisGirlFriday-1940",
        "poster": "https://archive.org/services/img/HisGirlFriday-1940",
        "sinopsis": "Un editor de periódico intenta evitar que su mejor reportera "
                    "(y exesposa) se case y abandone la profesión.",
        "caracteristicas": _features(comedia=1, romance=1, drama=1),
    },
    {
        "id": 16,
        "titulo": "Meet John Doe",
        "anio": 1941,
        "director": "Frank Capra",
        "genero": "Drama",
        "archive_id": "meet_john_doe",
        "poster": "https://archive.org/services/img/meet_john_doe",
        "sinopsis": "Una periodista inventa una carta de un tal 'John Doe' que desata "
                    "un movimiento social que pronto la supera.",
        "caracteristicas": _features(drama=1, romance=1),
    },
    {
        "id": 17,
        "titulo": "The Little Shop of Horrors",
        "anio": 1960,
        "director": "Roger Corman",
        "genero": "Comedia de terror",
        "archive_id": "TheLittleShopOfHorrors1960_765",
        "poster": "https://archive.org/services/img/TheLittleShopOfHorrors1960_765",
        "sinopsis": "Un torpe empleado de floristería cultiva una planta carnívora "
                    "que exige sangre humana. Comedia negra de culto.",
        "caracteristicas": _features(comedia=1, terror=1),
    },
]

# Índice rápido por id.
PELICULAS_POR_ID = {p["id"]: p for p in PELICULAS}


def obtener_pelicula(pelicula_id: int):
    """Devuelve los datos de una película por su id, o None si no existe."""
    return PELICULAS_POR_ID.get(pelicula_id)


def url_embed(pelicula_id: int) -> str:
    """URL del reproductor embebible de Internet Archive para esa película."""
    peli = PELICULAS_POR_ID.get(pelicula_id)
    if not peli:
        return ""
    return f"https://archive.org/embed/{peli['archive_id']}"
