"""
rule_override.py
────────────────
Two-layer override system:
  Layer 1 (keyword rules): hard/soft keyword matching per organ
  Layer 2 (problem→organ): uses problem_identifier scores to override
  
Both layers run; whichever produces the stronger signal wins.
"""

import re
from problem_identifier import identify_multiple_problems
from  organs_specification.rules import RULES, HARD_BOOST, SOFT_BOOST, SOFT_CAP
from  organs_specification.problem_to_organ import PROBLEM_TO_ORGAN, PROBLEM_THRESHOLD


# ── Layer x: Problem→organ mapping ───────────────────────────────────────────
# Only map to organs that actually EXIST in the 5-label set.
# "Mehnat va ish haqi" maps to adliya because Mehnat vazirligi is not a label —
# Adliya handles labour law disputes in the current label set.

# If problem score >= this, Layer x can fire


#it will normalize probabilities which individually each is out of 100. This function measures the factor which is 100 over total sum of all probabilties on the list of problem types of all 'murojaat's
def _normalize(probs: list) -> list:
    total = sum(p["prob"] for p in probs)
    if total == 0:
        return probs
    factor = 100.0 / total
    for p in probs:
        p["prob"] = round(p["prob"] * factor, 1)
    # Fix rounding drift
    diff = round(100.0 - sum(p["prob"] for p in probs), 1)
    if diff != 0:
        probs[0]["prob"] = round(probs[0]["prob"] + diff, 1)
    return probs


def apply_rule_override(text: str, prediction: str, probs: list) -> tuple:
    text_lower = text.lower() # make text all lovercase
    idx = {p["key"]: i for i, p in enumerate(probs)} # creates a set which key is the problem type and p is the probility of 'murojaat' belongs to that problem type.

    # ── Layer 1: keyword rules ────────────────────────────────────────────
    hard_fired = []
    for organ, rules in RULES.items():
        if organ not in idx:
            continue
        # Hard keywords: checks exicestance of hard rule words(single word is enough) from each organ in the text, if it exists, make probs[idx[organ]["prob"]]=max(probs[idx[organ]["prob"]],HARD_BOOST)
        for kw in rules["hard"]:
            if kw.lower() in text_lower:
                hard_fired.append(organ)

                probs[idx[organ]]["prob"] = max(probs[idx[organ]]["prob"], HARD_BOOST)
                
        # Soft keywords: 
        soft_hits = sum(1 for kw in rules["soft"] if kw.lower() in text_lower)
        if soft_hits > 0:
            boost = min(soft_hits * SOFT_BOOST, SOFT_CAP)
            probs[idx[organ]]["prob"] += boost

    probs = _normalize(probs)
    probs = sorted(probs, key=lambda x: x["prob"], reverse=True)
    idx = {p["key"]: i for i, p in enumerate(probs)}  # rebuild after sort
     
     #choosing max prediction after rules word checking( there could be probs[ids[c]]["probs"] which is not in hard_fired but has higher prediction score than any hard fired organ)
    layer1_prediction = (
        max(hard_fired, key=lambda c: probs[idx[c]]["prob"])
        if hard_fired else probs[0]["key"]
    )

    # ── Layer 2: problem_identifier override ─────────────────────────────
    # Only fires if it produces a STRONGER signal than layer 1, A
    problems = identify_multiple_problems(text)
    layer2_prediction = layer1_prediction

    if problems["categories"]:
        # Consider top-2 problems, map each to an organ, pick best
        candidate_organs = {}
        for prob_name, prob_score in problems["categories"][:2]:
            if prob_score >= PROBLEM_THRESHOLD and prob_name in PROBLEM_TO_ORGAN:
                organ = PROBLEM_TO_ORGAN[prob_name]
                # Track the highest problem score per organ
                if organ not in candidate_organs or prob_score > candidate_organs[organ]:
                    candidate_organs[organ] = prob_score

        if candidate_organs:
            # Boost each candidate organ proportionally
            for organ, score in candidate_organs.items():
                if organ in idx:
                    boost = score * 40.0   # proportional boost
                    probs[idx[organ]]["prob"] += boost

            probs = _normalize(probs)
            probs = sorted(probs, key=lambda x: x["prob"], reverse=True)
            layer2_prediction = probs[0]["key"]

    final_prediction = layer2_prediction
    return final_prediction, probs


# ── Demo ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import copy

    base_probs = [
        {"key": "adliya",           "label": {"name": "Adliya vazirligi"},             "prob": 26.9},
        {"key": "prokuratura",      "label": {"name": "Bosh prokuratura"},             "prob": 25.7},
        {"key": "soliq",            "label": {"name": "Soliq qo'mitasi"},              "prob": 22.7},
        {"key": "ichki_ishlar",     "label": {"name": "Ichki ishlar vazirligi"},       "prob": 14.5},
        {"key": "soglikni_saqlash", "label": {"name": "Sog'liqni saqlash vazirligi"}, "prob": 10.2},
    ]

    tests = [
        ("Mehnat + Kadastr (real murojaat)", """
            Hurmatli Adliya vaziri! Ushbu murojaatim orqali tumanimizdagi soliq va
            kadastr idoralarida tizimli ravishda davom etayotgan qonunbuzarliklar
            yuzasidan yordam berishingizni so'rayman. Birinchidan, men ishlaydigan
            davlat tashkilotida Mehnat kodeksi qo'pol ravishda buzilmoqda. Xodimlar
            dam olish kunlari va kechki soat 18:00 dan keyin ham rasmiy buyruqsiz
            ishlashga majburlanmoqda. Bu ortiqcha ish vaqtlari uchun hech qanday
            haq to'lanmaydi. Ikkinchidan, otamdan qolgan uy-joyni tuman Davlat
            xizmatlari markazi (DXM) orqali kadastr qilish uchun 3 marta ariza
            topshirdim. Biroq, tuman kadastr bo'limi hech qanday qonuniy asoslarsiz
            arizalarimni rad etib kelmoqda.
        """),
        ("Korrupsiya shikoyati", "Politsiya xodimi pora talab qildi, korrupsiya haqida shikoyat qilmoqchiman."),
        ("Soliq masalasi", "Soliq deklaratsiyamni topshirish muddatini o'tkazib yubordim, QQS bo'yicha savol bor."),
        ("Tibbiy muammo", "Bolam uchun emlash sertifikatini olishda muammo bor, shifokor yordam bermayapti."),
        ("Nikoh hujjati", "Nikoh guvohnomamni yo'qotdim, notarius orqali tiklash kerak."),
    ]

    print("=" * 65)
    for title, text in tests:
        p = copy.deepcopy(base_probs)
        pred, new_probs = apply_rule_override(text, "adliya", p)
        print(f"\n{title}")
        print(f"  => {pred}")
        for item in new_probs:
            bar = "█" * int(item['prob'] / 5)
            print(f"     {item['prob']:5.1f}%  {bar:<20}  {item['key']}")
    print("=" * 65)