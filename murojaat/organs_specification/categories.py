UZ_STOPWORDS = {
    "men", "sen", "u", "biz", "siz", "ular", "bu", "shu", "o'sha",
    "va", "yoki", "ham", "lekin", "ammo", "chunki", "agar",
    "bilan", "uchun", "dan", "ga", "da", "ni", "ning",
    "edi", "ekan", "emish", "bo'ldi", "bo'lsa", "bo'lib",
    "qildi", "qilsa", "qilib", "oldi", "berdi",
    "bor", "yo'q", "kerak", "zarur", "lozim",
    "qanday", "qancha", "qachon", "qayerda", "qayerga", "nima", "kim",
    "muammo", "savol", "ariza", "xabar", "haqida", "bo'yicha",
    "hurmatli", "iltimos", "murojaat", "sizdan", "mening",
}

# ── Category definitions ─────────────────────────────────────────────────────
# penalty: ONLY penalise when the word is truly impossible in this category
# (e.g. "shifoxona" cannot be in a tax complaint). Do NOT cross-penalise
# categories that realistically co-occur (mehnat ↔ kadastr, soliq ↔ kadastr).
#Making separete text file for this
CATEGORIES = {
    "Mehnat va ish haqi": {
        "must":    ["ish haqi", "mehnat shartnomasi", "ishdan bo'shatish",
                    "mehnat kodeksi", "ish beruvchi", "xodim", "maosh",
                    "mehnat inspeksiyasi", "ortiqcha ish", "majburiy ishlatish",
                    "dam olish kunlari", "ish vaqti"],
        "support": ["to'lanmaydi", "noqonuniy bo'shatish",
                    "ta'til", "kamsitish", "kasaba",
                    "mehnat daftarchasi", "ijtimoiy sug'urta"],
        "penalty": ["shifoxona", "emlash", "shifokor"],   # meditsina faqat
        "weight":  3.0,
    },
    "Uy-joy va ro'yxatga olish / kadastr": {
        "must":    ["kadastr", "propiska", "ro'yxatga olish", "uy-joy",
                    "kvartira", "yer uchastkasi", "mulkni ro'yxatdan",
                    "dxm", "ko'chmas mulk", "uy joyi"],
        "support": ["ijara", "ko'p qavatli", "meros mulk", "uy sotib",
                    "ipoteka", "qurilish", "hovli", "yashash joyi",
                    "davlat xizmatlari markazi"],
        "penalty": ["shifoxona", "emlash", "shifokor"],
        "weight":  3.0,
    },
    "Tibbiy muammo / davolanish": {
        "must":    ["shifoxona", "shifokor", "poliklinika", "tashxis",
                    "davolanish", "operatsiya", "emlash", "dori",
                    "tibbiy", "bemor", "kasallik", "vrach"],
        "support": ["yo'llanma", "sanatoriya", "retsept", "apteka",
                    "reabilitatsiya", "tez yordam", "tibbiy xato"],
        "penalty": [],   # tibbiy hamma yerda bo'lishi mumkin emas, lekin jarima yo'q
        "weight":  3.0,
    },
    "Soliq va moliyaviy masalalar": {
        "must":    ["soliq", "qqs", "deklaratsiya", "soliq inspeksiyasi",
                    "soliq qarzi", "patent", "hisob-faktura",
                    "soliq ro'yxati", "nalog", "bojxona"],
        "support": ["daromad solig'i", "yagona ijtimoiy to'lov",
                    "elektron imzo buxgalteriya", "mulk solig'i",
                    "transport solig'i", "jarima soliq"],
        "penalty": ["shifoxona", "shifokor"],
        "weight":  3.0,
    },
    "Huquqbuzarlik / korrupsiya": {
        "must":    ["korrupsiya", "pora", "mansabdor",
                    "huquqbuzarlik", "noqonuniy asoslarsiz",
                    "firibgarlik", "mansabini suiiste'mol",
                    "qonunbuzarlik"],
        "support": ["tergov", "prokuratura", "hibsga",
                    "sud qaroridan", "ayblov", "guvoh", "jinoyat"],
        "penalty": ["shifoxona"],
        "weight":  2.5,
    },
    "Hujjat rasmiylashtirish": {
        "must":    ["pasport", "nikoh guvohnomasi",
                    "tug'ilganlik haqidagi", "id karta",
                    "fuqarolik holati", "notarius", "vasiyat",
                    "guvohnoma yo'qotdim"],
        "support": ["rasmiylashtirish", "tasdiqlash", "legalizatsiya",
                    "apostil", "hujjat topshirish"],
        "penalty": ["shifoxona", "kadastr"],
        "weight":  2.5,
    },
    "Ta'lim muammosi": {
        "must":    ["maktab", "universitet", "o'quvchi", "talaba",
                    "o'qituvchi", "stipendiya", "diplom",
                    "bolalar bog'chasi", "ta'lim muassasasi"],
        "support": ["imtihon", "attestat", "inklyuziv", "darslik", "sinf"],
        "penalty": ["shifoxona", "kadastr", "soliq"],
        "weight":  2.5,
    },
    "Ekologiya / sanitariya": {
        "must":    ["ekologiya", "ifloslantirish", "chiqindi",
                    "atrof-muhit", "sanitariya", "zaharlanish",
                    "tutun chiqarish", "o'rmon kesish"],
        "support": ["daryo iflos", "tuproq", "baliq qirg'ini",
                    "axlat poligoni", "sanoat zavod"],
        "penalty": ["shifoxona", "soliq", "kadastr"],
        "weight":  2.5,
    },
    "Ijtimoiy nafaqa / yordam": {
        "must":    ["pensiya", "ijtimoiy yordam", "ko'p bolali oila",
                    "ijtimoiy ta'minot", "subsidiya", "ishsizlik nafaqasi",
                    "bola nafaqasi"],
        "support": ["moddiy yordam", "keksalar", "qashshoq", "yetim"],
        "penalty": ["shifoxona", "kadastr", "soliq"],
        "weight":  2.5,
    },
    "Transport / haydovchilik": {
        "must":    ["haydovchilik guvohnomasi", "avtomobil ro'yxat",
                    "avtohalokat", "yo'l-patrull", "ypx shtraf",
                    "transport vositasi ro'yxat"],
        "support": ["raqam belgisi", "texosmotr", "yo'l qoidasi"],
        "penalty": ["shifoxona", "soliq", "kadastr"],
        "weight":  2.5,
    },
}