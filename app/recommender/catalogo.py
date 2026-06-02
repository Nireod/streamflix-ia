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
    suspenso, cine_negro, aventura, mudo, clasico_pre1940
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
    "aventura",
    "mudo",
    "clasico_pre1940",
]


def _features(**kwargs):
    """Construye el vector de características poniendo en 1 las indicadas."""
    return {c: (1 if kwargs.get(c) else 0) for c in CARACTERISTICAS}


def _peli(id, titulo, anio, director, genero, archive_id, sinopsis, **caract):
    """Atajo para declarar una película de forma compacta."""
    return {
        "id": id,
        "titulo": titulo,
        "anio": anio,
        "director": director,
        "genero": genero,
        "archive_id": archive_id,
        "poster": f"https://archive.org/services/img/{archive_id}",
        "sinopsis": sinopsis,
        "caracteristicas": _features(**caract),
    }


# id interno -> datos. El campo archive_id es el identificador REAL en archive.org.
PELICULAS = [
    # ---------------- Terror ----------------
    _peli(1, "Nosferatu", 1922, "F. W. Murnau", "Terror", "Nosferatu1922",
          "El conde Orlok, un vampiro de Transilvania, siembra el terror en una "
          "ciudad alemana. Obra maestra del cine expresionista.",
          terror=1, suspenso=1, mudo=1, clasico_pre1940=1),
    _peli(2, "El gabinete del Dr. Caligari", 1920, "Robert Wiene", "Terror",
          "DasKabinettdesDoktorCaligariTheCabinetofDrCaligari",
          "Un hipnotizador usa a un sonámbulo para cometer asesinatos. Pieza "
          "fundamental del expresionismo alemán.",
          terror=1, suspenso=1, mudo=1, clasico_pre1940=1),
    _peli(3, "El fantasma de la ópera", 1925, "Rupert Julian", "Terror",
          "ThePhantomOfTheOpera1925NewYorkGeneralReleasePrint_620",
          "Un misterioso fantasma que habita la Ópera de París se obsesiona con "
          "una joven cantante.",
          terror=1, drama=1, romance=1, mudo=1, clasico_pre1940=1),
    _peli(4, "La noche de los muertos vivientes", 1968, "George A. Romero", "Terror",
          "night-of-the-living-dead-1968-english",
          "Un grupo de personas se refugia en una granja mientras los muertos "
          "regresan a la vida. Fundó el cine moderno de zombis.",
          terror=1, suspenso=1),
    _peli(5, "Carnival of Souls", 1962, "Herk Harvey", "Terror", "CarnivalOfSouls1962",
          "Tras un accidente, una mujer se siente atraída por un pabellón "
          "abandonado y perseguida por figuras espectrales.",
          terror=1, suspenso=1, drama=1),
    _peli(6, "House on Haunted Hill", 1959, "William Castle", "Terror",
          "HouseOnHauntedHill1959",
          "Un millonario excéntrico ofrece dinero a cinco invitados si sobreviven "
          "una noche en una mansión embrujada.",
          terror=1, suspenso=1),
    _peli(7, "White Zombie", 1932, "Victor Halperin", "Terror", "WhiteZombie1932",
          "En Haití, un hacendado recurre a un brujo vudú para convertir en zombi "
          "a la mujer que ama. Considerada la primera película de zombis.",
          terror=1, suspenso=1, clasico_pre1940=1),
    _peli(8, "The Last Man on Earth", 1964, "Ubaldo Ragona", "Terror",
          "the-last-man-on-earth-1964-with-vincent-price-de-oldify",
          "El último humano sobrevive en un mundo de vampiros. Vincent Price "
          "protagoniza esta adaptación de 'Soy leyenda'.",
          terror=1, ciencia_ficcion=1, drama=1, suspenso=1),
    _peli(9, "Dementia 13", 1963, "Francis Ford Coppola", "Terror",
          "Dementia13withSpanishSubtitles",
          "Una viuda ambiciosa se ve envuelta en una serie de asesinatos con "
          "hacha en un castillo irlandés.",
          terror=1, suspenso=1),
    _peli(10, "The Bat", 1959, "Crane Wilbur", "Terror", "PhantasmagoriaTheater-TheBat1959653",
          "Una escritora de misterio y un asesino enmascarado buscan una fortuna "
          "oculta en una mansión. Con Vincent Price.",
          terror=1, suspenso=1),
    _peli(11, "Bluebeard", 1944, "Edgar G. Ulmer", "Terror",
          "1944-bluebeard-barbazul-edgar-g.-ulmer-ve_202012",
          "Un titiritero parisino esconde un oscuro secreto: estrangula a las "
          "mujeres que pinta.",
          terror=1, suspenso=1, drama=1),
    _peli(12, "Maniac", 1934, "Dwain Esper", "Terror", "maniac-1934",
          "Un antiguo actor de vodevil ayuda a un científico loco y desciende a "
          "la demencia. Cine de explotación de culto.",
          terror=1, suspenso=1, clasico_pre1940=1),
    _peli(13, "The Vampire Bat", 1933, "Frank R. Strayer", "Terror", "TheVampireBat",
          "Una aldea europea atribuye una serie de muertes a un vampiro, pero la "
          "verdad es más siniestra.",
          terror=1, suspenso=1, clasico_pre1940=1),

    # ---------------- Ciencia ficción ----------------
    _peli(14, "Metropolis", 1927, "Fritz Lang", "Ciencia ficción", "Metropolis1927EnglishVersion",
          "En una ciudad futurista dividida en clases, un joven y una obrera "
          "intentan reconciliar a trabajadores y dirigentes.",
          ciencia_ficcion=1, drama=1, mudo=1, clasico_pre1940=1),
    _peli(15, "Plan 9 from Outer Space", 1959, "Ed Wood", "Ciencia ficción",
          "774-plan-9-from-outer-space",
          "Alienígenas resucitan a los muertos para frenar a la humanidad. "
          "Célebre película de culto de serie B.",
          ciencia_ficcion=1, terror=1),
    _peli(16, "The Phantom Planet", 1961, "William Marshall", "Ciencia ficción", "Phantom_Planet",
          "Un astronauta aterriza en un asteroide habitado por seres diminutos y "
          "queda atrapado en sus conflictos.",
          ciencia_ficcion=1, aventura=1),
    _peli(17, "Teenagers from Outer Space", 1959, "Tom Graeff", "Ciencia ficción",
          "teenagers_from_outerspace",
          "Alienígenas adolescentes llegan a la Tierra para criar monstruos "
          "gigantes como ganado.",
          ciencia_ficcion=1, terror=1),
    _peli(18, "First Spaceship on Venus", 1960, "Kurt Maetzig", "Ciencia ficción",
          "FirstSpaceshipOnVenusMPEG",
          "Una expedición internacional viaja a Venus tras descubrir un mensaje "
          "alienígena. Ciencia ficción de la Guerra Fría.",
          ciencia_ficcion=1, aventura=1, drama=1),
    _peli(19, "Things to Come", 1936, "William Cameron Menzies", "Ciencia ficción",
          "things-to-come",
          "Un siglo de guerra, colapso y renacimiento tecnológico de la "
          "humanidad, según la visión de H. G. Wells.",
          ciencia_ficcion=1, drama=1, clasico_pre1940=1),
    _peli(20, "The Lost World", 1925, "Harry O. Hoyt", "Ciencia ficción", "TheLostWorld512",
          "Una expedición descubre una meseta donde aún viven dinosaurios. "
          "Pionera de los efectos especiales con stop-motion.",
          ciencia_ficcion=1, aventura=1, mudo=1, clasico_pre1940=1),
    _peli(21, "Voyage to the Planet of Prehistoric Women", 1968, "Peter Bogdanovich",
          "Ciencia ficción", "VoyagetothePlanetofPrehistoricWomen",
          "Astronautas exploran Venus y encuentran una raza de mujeres y "
          "criaturas prehistóricas.",
          ciencia_ficcion=1, aventura=1),

    # ---------------- Comedia ----------------
    _peli(22, "La quimera del oro", 1925, "Charles Chaplin", "Comedia", "the-gold-rush-film-1925",
          "Charlot busca fortuna en Alaska durante la fiebre del oro, entre "
          "aventuras, hambre y amor.",
          comedia=1, romance=1, aventura=1, mudo=1, clasico_pre1940=1),
    _peli(23, "El maquinista de La General", 1926, "Buster Keaton", "Comedia", "TheGeneral_201312",
          "Un maquinista persigue a los soldados que robaron su locomotora "
          "durante la Guerra Civil estadounidense.",
          comedia=1, accion=1, aventura=1, mudo=1, clasico_pre1940=1),
    _peli(24, "El moderno Sherlock Holmes", 1924, "Buster Keaton", "Comedia", "MyMovie_20190318",
          "Un proyeccionista que sueña con ser detective se mete literalmente "
          "dentro de la película que proyecta.",
          comedia=1, romance=1, mudo=1, clasico_pre1940=1),
    _peli(25, "His Girl Friday", 1940, "Howard Hawks", "Comedia", "his_girl_friday",
          "Un editor de periódico intenta evitar que su mejor reportera (y "
          "exesposa) se case y abandone la profesión.",
          comedia=1, romance=1, drama=1),
    _peli(26, "The Little Shop of Horrors", 1960, "Roger Corman", "Comedia",
          "TheLittleShopOfHorrors1960_765",
          "Un torpe empleado de floristería cultiva una planta carnívora que "
          "exige sangre humana. Comedia negra de culto.",
          comedia=1, terror=1),
    _peli(27, "Steamboat Bill, Jr.", 1928, "Buster Keaton", "Comedia", "steamboat_bill_ipod",
          "El hijo afeminado de un rudo capitán de barco fluvial debe ganarse su "
          "respeto en plena tormenta. Famosa por sus acrobacias.",
          comedia=1, romance=1, aventura=1, mudo=1, clasico_pre1940=1),
    _peli(28, "El chico", 1921, "Charles Chaplin", "Comedia", "Brzdac1921",
          "Charlot adopta a un niño abandonado y forma con él una entrañable "
          "familia. Comedia y drama a partes iguales.",
          comedia=1, drama=1, mudo=1, clasico_pre1940=1),
    _peli(29, "The Immigrant", 1917, "Charles Chaplin", "Comedia",
          "CharlieChaplinTheImmigrant1917HD_201808",
          "Charlot emigra a Estados Unidos en barco y enfrenta los apuros de "
          "llegar sin dinero a una tierra nueva.",
          comedia=1, romance=1, mudo=1, clasico_pre1940=1),
    _peli(30, "My Man Godfrey", 1936, "Gregory La Cava", "Comedia", "MyManGodfrey1936",
          "Una joven rica contrata como mayordomo a un 'vagabundo' que resulta "
          "tener más clase que toda su familia.",
          comedia=1, romance=1, clasico_pre1940=1),
    _peli(31, "Africa Screams", 1949, "Charles Barton", "Comedia",
          "africascreams1949abbottandcostello1h19m480p",
          "Abbott y Costello se embarcan en un disparatado safari por África "
          "tras un mapa del tesoro.",
          comedia=1, aventura=1),
    _peli(32, "Royal Wedding", 1951, "Stanley Donen", "Comedia", "royalwedding1951film",
          "Una pareja de hermanos bailarines actúa en Londres durante la boda "
          "real. Famosa por el número de Fred Astaire bailando en el techo.",
          comedia=1, romance=1),

    # ---------------- Drama ----------------
    _peli(33, "El acorazado Potemkin", 1925, "Serguéi Eisenstein", "Drama", "BattleshipPotemkin",
          "La tripulación de un acorazado se amotina contra sus oficiales. "
          "Célebre por la secuencia de la escalinata de Odesa.",
          drama=1, accion=1, mudo=1, clasico_pre1940=1),
    _peli(34, "Meet John Doe", 1941, "Frank Capra", "Drama", "meet_john_doe",
          "Una periodista inventa una carta de un tal 'John Doe' que desata un "
          "movimiento social que pronto la supera.",
          drama=1, romance=1),
    _peli(35, "A Farewell to Arms", 1932, "Frank Borzage", "Drama", "afarewelltoarms1932garycooper",
          "Romance trágico entre un soldado y una enfermera durante la Primera "
          "Guerra Mundial. Basada en Hemingway.",
          drama=1, romance=1, clasico_pre1940=1),
    _peli(36, "Of Human Bondage", 1934, "John Cromwell", "Drama",
          "of.-human.-bondage.-1934.1080p.-blu-ray.-h-264.-aac-rarbg",
          "Un estudiante de medicina queda obsesionado con una camarera "
          "manipuladora. Lanzó a la fama a Bette Davis.",
          drama=1, romance=1, clasico_pre1940=1),
    _peli(37, "A Star Is Born", 1937, "William A. Wellman", "Drama", "AStarIsBorn1937FullHDMovie",
          "Una joven aspirante a actriz triunfa en Hollywood mientras la carrera "
          "de su marido se hunde.",
          drama=1, romance=1, clasico_pre1940=1),
    _peli(38, "Penny Serenade", 1941, "George Stevens", "Drama", "PennySerenade1941_201711",
          "Una pareja recuerda los altibajos de su matrimonio y su lucha por "
          "formar una familia. Con Cary Grant e Irene Dunne.",
          drama=1, romance=1),
    _peli(39, "Made for Each Other", 1939, "John Cromwell", "Drama",
          "madeforeachother1939carolelombard",
          "Un joven matrimonio enfrenta las presiones económicas y familiares de "
          "la vida real. Con James Stewart y Carole Lombard.",
          drama=1, romance=1, clasico_pre1940=1),
    _peli(40, "The Snows of Kilimanjaro", 1952, "Henry King", "Drama",
          "thesnowsofkilimanjarofullmoviegreatquality1952",
          "Un escritor herido en un safari africano repasa su vida y sus amores "
          "mientras lucha por sobrevivir. Basada en Hemingway.",
          drama=1, romance=1, aventura=1),
    _peli(41, "The Little Princess", 1939, "Walter Lang", "Drama",
          "the-little-princess-shirley-temple-1939-hd-quality-musical-comedy",
          "Una niña es enviada a un internado y, al desaparecer su padre en la "
          "guerra, pasa de privilegiada a sirvienta. Con Shirley Temple.",
          drama=1, clasico_pre1940=1),
    _peli(42, "Till the Clouds Roll By", 1946, "Richard Whorf", "Drama", "till_the_clouds_roll_by",
          "Biografía musical del compositor Jerome Kern, con grandes números "
          "musicales de la MGM.",
          drama=1, romance=1),

    # ---------------- Cine negro / Suspenso ----------------
    _peli(43, "Detour", 1945, "Edgar G. Ulmer", "Cine negro", "detour-1945",
          "Un pianista que cruza el país haciendo autostop se ve atrapado en una "
          "espiral de muerte y chantaje.",
          cine_negro=1, drama=1, suspenso=1),
    _peli(44, "Scarlet Street", 1945, "Fritz Lang", "Cine negro", "ScarletStreet",
          "Un cajero de mediana edad se obsesiona con una mujer que lo manipula a "
          "él y a su pintura.",
          cine_negro=1, drama=1, romance=1, suspenso=1),
    _peli(45, "D.O.A.", 1950, "Rudolph Maté", "Cine negro", "DOA1950",
          "Un hombre envenenado tiene pocas horas de vida para descubrir quién lo "
          "asesinó… y por qué.",
          cine_negro=1, suspenso=1),
    _peli(46, "The Stranger", 1946, "Orson Welles", "Cine negro",
          "1946-the-stranger-el-extrano-orson-welles-vo",
          "Un investigador persigue a un criminal de guerra nazi oculto como "
          "profesor en un pueblo de Nueva Inglaterra.",
          cine_negro=1, suspenso=1, drama=1),
    _peli(47, "The Hitch-Hiker", 1953, "Ida Lupino", "Cine negro", "IdaLupinostheHitch-hiker1953",
          "Dos amigos de pesca son secuestrados por un asesino que hace "
          "autostop. Dirigida por Ida Lupino.",
          cine_negro=1, suspenso=1),
    _peli(48, "Kansas City Confidential", 1952, "Phil Karlson", "Cine negro", "kansascityconfidencial",
          "Un exconvicto inocente debe limpiar su nombre tras un atraco "
          "perfectamente planeado.",
          cine_negro=1, suspenso=1, accion=1),
    _peli(49, "He Walked by Night", 1948, "Alfred L. Werker", "Cine negro", "He_Walked_By_Night.avi",
          "La policía de Los Ángeles da caza a un astuto asesino. Inspiró la "
          "serie 'Dragnet'.",
          cine_negro=1, suspenso=1),
    _peli(50, "Beat the Devil", 1953, "John Huston", "Cine negro", "BeatTheDevil1953",
          "Un grupo de estafadores varados intriga por unas tierras ricas en "
          "uranio. Comedia negra con Humphrey Bogart.",
          cine_negro=1, comedia=1, aventura=1),
    _peli(51, "Gaslight", 1940, "Thorold Dickinson", "Suspenso", "gaslight-1940-restored-movie-720p-hd",
          "Un marido manipula a su esposa para hacerle creer que está perdiendo "
          "la cordura. Origen del término 'gaslighting'.",
          suspenso=1, drama=1, clasico_pre1940=1),
    _peli(52, "Suddenly", 1954, "Lewis Allen", "Suspenso",
          "suddenly-1954-movie-trailer-frank-sinatra-sterling-hayden",
          "Un asesino a sueldo toma una casa para atentar contra el presidente. "
          "Con Frank Sinatra.",
          suspenso=1, cine_negro=1, drama=1),
    _peli(53, "The Big Lift", 1950, "George Seaton", "Drama", "The_Big_Lift",
          "Dos sargentos estadounidenses participan en el puente aéreo de Berlín "
          "durante la posguerra. Con Montgomery Clift.",
          drama=1, romance=1),

    # ---------------- Aventura ----------------
    _peli(54, "Robin Hood", 1922, "Allan Dwan", "Aventura", "ROBINHOOD1922WithSYMPHONICSCORE",
          "El conde de Huntingdon se convierte en Robin Hood para luchar contra "
          "la tiranía. Con Douglas Fairbanks.",
          aventura=1, accion=1, romance=1, mudo=1, clasico_pre1940=1),
    _peli(55, "La marca del Zorro", 1920, "Fred Niblo", "Aventura", "vidzo",
          "Un noble californiano lleva una doble vida como el justiciero "
          "enmascarado El Zorro. Con Douglas Fairbanks.",
          aventura=1, accion=1, romance=1, mudo=1, clasico_pre1940=1),
    _peli(56, "El ladrón de Bagdad", 1924, "Raoul Walsh", "Aventura", "vidtb",
          "Un ladrón se enamora de una princesa y emprende una fantástica "
          "búsqueda para conquistarla. Con Douglas Fairbanks.",
          aventura=1, romance=1, mudo=1, clasico_pre1940=1),
    _peli(57, "Father Brown, Detective", 1954, "Robert Hamer", "Aventura",
          "father-brown-the-detective-1954-mys.-detec.-alec-guiness",
          "Un sacerdote detective persigue a un ladrón de arte por toda Europa. "
          "Con Alec Guinness.",
          aventura=1, comedia=1, suspenso=1),
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
