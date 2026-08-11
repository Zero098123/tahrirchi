from flask import Flask, render_template, request

from problem_identifier import identify_multiple_problems
from rule_override import apply_rule_override
from skops.io import dump, loads, get_untrusted_types

app = Flask(__name__)

with open('uzbek_gov_classifier.skops', 'rb') as f:
    # skops loads() takes bytes, not a file object ✅
    raw = f.read()
unknown_types = get_untrusted_types(data=raw)
print("Trusting types:", unknown_types)
model = loads(raw, trusted=unknown_types)

LABELS = {
    'adliya':           {'name': 'Adliya vazirligi',             'icon': '⚖️'},
    'prokuratura':      {'name': 'Bosh prokuratura',             'icon': '🏛️'},
    'soliq':            {'name': "Soliq qo'mitasi",              'icon': '🧾'},
    'ichki_ishlar':     {'name': 'Ichki ishlar vazirligi',       'icon': '🛡️'},
    'soglikni_saqlash': {'name': "Sog'liqni saqlash vazirligi",  'icon': '🏥'},
}

@app.route('/')
def home():
    return render_template('index.html', labels=LABELS)

@app.route('/predict', methods=['POST'])
def predict():
    text = request.form['appeal_text']

    # ── Step 1: Base model prediction ────────────────────────────────────────
    prediction   = model.predict([text])[0]
    probabilities = model.predict_proba([text])[0]
    classes      = model.classes_

    probs = sorted(
        [
            {
                'key':   classes[i],
                'label': LABELS[classes[i]],
                'prob':  round(float(probabilities[i]) * 100, 1),
            }
            for i in range(len(classes))
        ],
        key=lambda x: x['prob'],
        reverse=True,
    )

    # ── Step 2: Rule-based override ──────────────────────────────────────────
    prediction, probs = apply_rule_override(text, prediction, probs)

    # ── Step 3: Multi-problem identification (normalised to 100 %) ───────────
    problem_data = identify_multiple_problems(text, threshold=0.18)
    raw_cats     = problem_data['categories']   # [(name, score), ...]

    total_score = sum(score for _, score in raw_cats)

    if total_score > 0:
        detected_categories = [
            {
                'name':       cat,
                'confidence': round((score / total_score) * 100, 1),
            }
            for cat, score in raw_cats
        ]
    else:
        detected_categories = []

    return render_template(
        'index.html',
        labels=LABELS,
        prediction=prediction,
        pred_label=LABELS[prediction],
        probabilities=probs,
        original_text=text,
        keywords=problem_data['keywords'],
        detected_categories=detected_categories,
        primary_problem=problem_data['primary_problem'],
    )

if __name__ == '__main__':
    app.run(debug=True)