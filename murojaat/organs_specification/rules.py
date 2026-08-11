RULES = {
    "adliya": {
        "hard": [
            "nikoh guvohnoma", "tug'ilganlik guvohnoma", "vafot etganlik guvohnoma",
            "notarial tasdiqlash", "notarius", "yuridik shaxsni tugatish",
            "vasiylik", "homiylik", "fuqarolikdan chiqish",
            "da'vo ariza", "meros rasmiylashtirish", "ajralish",
            "kadastr qilish", "mulkni ro'yxatdan", "uy-joyni",
            "dxm orqali", "davlat xizmatlari markazi",
        ],
        "soft": [
            "adliya", "yuridik yordam", "fuqarolik holati",
            "shartnoma", "notarial", "hujjat rasmiylashtirish",
        ],
    },
    "prokuratura": {
        "hard": [
            "korrupsiya", "pora", "prokuratura", "tergov",
            "jinoiy ish", "noqonuniy qamoq", "hibsga olingan",
            "davlat mulkini o'g'irlash", "yolg'on ko'rsatuv",
            "mansabdor shaxs jinoyat",
        ],
        "soft": [
            "noqonuniy", "qonunbuzarlik", "fosh", "tahdid",
            "sud ijrochisi", "ayblov",
        ],
    },
    "soliq": {
        "hard": [
            "QQS", "soliq deklaratsiya", "soliq qarzi",
            "soliq inspeksiya", "soliq ro'yxat", "patent asosida",
            "yakka tartibdagi tadbirkor", "dividend solig'i",
            "elektron hisob-faktura", "bojxona yig'im",
        ],
        "soft": [
            "deklaratsiya", "tadbirkor", "buxgalteriya",
            "elektron imzo", "patent", "maosh solig'i",
        ],
    },
    "ichki_ishlar": {
        "hard": [
            "haydovchilik guvohnoma", "biometrik pasport",
            "yo'l-patrull", "avtomobil ro'yxat", "propiska",
            "oilaviy zo'ravonlik", "xorijiy fuqaro viza",
            "ID karta", "jamoat tartib", "zagran pasport", "qizil pasport",
            "Xorijiy pasport"
        ],
        "soft": [
            "pasport", "politsiya", "ro'yxatga olish",
            "transport vosita", "jinoyat", "o'g'ri",
        ],
    },
    "soglikni_saqlash": {
        "hard": [
            "emlash", "vaksinatsiya", "COVID-19 sertifikat",
            "nogironlik guruhi", "tibbiy komissiya",
            "sanatoriya yo'llanma", "ruhiy salomatlik",
            "tez tibbiy yordam", "tibbiy sug'urta", "dori retsept",
        ],
        "soft": [
            "shifoxona", "shifokor", "poliklinika",
            "dori", "tibbiy", "kasallik", "homilador",
        ],
    },
}

HARD_BOOST = 60.0   # hard keyword → floor at this raw prob value
SOFT_BOOST = 12.0   # per soft keyword hit (capped)
SOFT_CAP   = 30.0   # max total soft boost per organ
