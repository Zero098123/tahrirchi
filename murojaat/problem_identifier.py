"""
problem_identifier.py  —  Multi-problem detector for Uzbek government appeals
"""
import re
import numpy as np
from organs_specification.categories import UZ_STOPWORDS, CATEGORIES

#Making separete text file for this common unimportant words

from text_utils import normalize_text, phrase_in_text,normalize_apostrophes
#counts how many phrases exists in text.
def _phrase_hits(text: str, phrases: list) -> int:
    return sum(1 for p in phrases if phrase_in_text(p, text))

#identifying problems that included in 'murojaat' meaning.
def identify_multiple_problems(text: str, threshold: float = 0.10) -> dict:
    """
    Returns categories with normalised scores.
    Uses linear (L1) normalization — not softmax — so two equally strong
    problems each get ~50%, not 2%/98%.
    A category is shown only if its raw score >= MIN_RAW_SCORE,
    preventing weak coincidental matches from appearing.
    """
    MIN_RAW_SCORE = 2.0   # must score at least this before normalisation
    text_norm = normalize_text(text)          # normalize ONCE, reuse below

    raw: dict[str, float] = {}
    for cat, cfg in CATEGORIES.items():
        must    = _phrase_hits(text_norm, cfg["must"])
        support = _phrase_hits(text_norm, cfg["support"])
        penalty = _phrase_hits(text_norm, cfg["penalty"])

        score = must * cfg["weight"] + support * 0.6 - penalty * 0.5
        if score >= MIN_RAW_SCORE:
            raw[cat] = score

    # ── Linear normalisation (proportional) ─────────────────────────────────
    if raw:
        total = sum(raw.values())
        normalised = {k: v / total for k, v in raw.items()}
        categories = sorted(
            [(k, round(v, 4)) for k, v in normalised.items() if v >= threshold],
            key=lambda x: x[1], reverse=True,
        )
    else:
        categories = []

    # keyword extraction
    text_apos = normalize_apostrophes(text)
    tokens = re.split(r"[\s,;.!?()\[\]«»\"]+", text_apos)   # ' removed from split chars
    keywords = [
        t for t in tokens
        if len(t) > 2 and t.strip("'").lower() not in UZ_STOPWORDS
    ]
    return {
        "keywords":        keywords,
        "categories":      categories,
        "primary_problem": categories[0][0] if categories else "Aniqlanmadi",
    }


if __name__ == "__main__":
    tests = [
        ("Ish haqi + Kadastr (ikki muammo)", """
            Hurmatli Adliya vaziri! Ushbu murojaatim orqali tumanimizdagi soliq va
            kadastr idoralarida tizimli ravishda davom etayotgan qonunbuzarliklar
            yuzasidan yordam berishingizni so'rayman.
            Birinchidan, men ishlaydigan davlat tashkilotida Mehnat kodeksi qo'pol
            ravishda buzilmoqda. Xodimlar dam olish kunlari va kechki soat 18:00 dan
            keyin ham rasmiy buyruqsiz ishlashga majburlanmoqda. Bu ortiqcha ish
            vaqtlari uchun hech qanday haq to'lanmaydi.
            Ikkinchidan, otamdan qolgan uy-joyni tuman Davlat xizmatlari markazi
            (DXM) orqali kadastr qilish uchun 3 marta ariza topshirdim. Biroq,
            tuman kadastr bo'limi hech qanday qonuniy asoslarsiz, sun'iy ravishda
            arizalarimni rad etib kelmoqda.
        """),
        ("Bitta muammo: hujjat", """
            Pasportimni yo'qotdim. Tug'ilganlik haqidagi guvohnomam ham yo'q.
            Notarius hujjatni tasdiqlashdan bosh tortdi.
        """),
        ("Uch muammo: tibbiy + soliq + ish haqi", """
            Shifoxonada noto'g'ri tashxis qo'yildi. Shuningdek soliq inspeksiyasi
            asossiz jarima qo'lladi. Ish beruvchi ish haqimni to'lamayapti,
            mehnat kodeksi buzilmoqda.
        """),
    ]

    for title, text in tests:
        r = identify_multiple_problems(text)
        print(f"\n{'='*60}\n{title}")
        for cat, sc in r["categories"]:
            bar = "█" * int(sc * 30)
            print(f"  {sc*100:5.1f}%  {bar:<30}  {cat}")
        print(f"  Asosiy: {r['primary_problem']}")