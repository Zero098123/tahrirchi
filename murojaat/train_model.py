import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from skops.io import dump, loads, get_untrusted_types



# ── Synthetic training data ───────────────────────────────────────────────────
# 5 government bodies:
#   1. adliya          – Adliya vazirligi (Ministry of Justice)
#   2. prokuratura     – Bosh prokuratura (Prosecutor's Office)
#   3. soliq           – Soliq qo'mitasi (Tax Committee)
#   4. ichki_ishlar    – Ichki ishlar vazirligi (Ministry of Internal Affairs)
#   5. soglikni_saqlash – Sog'liqni saqlash vazirligi (Ministry of Health)

import os

DATA_DIR = "data"

#preparing processable data from 'data' package.
data = []
for filename in os.listdir(DATA_DIR):
    if filename.endswith(".txt"):
        category = filename.replace(".txt", "").lower()
        filepath = os.path.join(DATA_DIR, filename)
        with open(filepath, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    data.append((line, category))
df = pd.DataFrame(data, columns=["text", "category"])

print("Categories:", df["category"].unique())
print("Total samples:", len(df))
print(df["category"].value_counts())
print()

# ── Train / test split ────────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    df["text"], df["category"], test_size=0.2, random_state=42, stratify=df["category"]
)
# RANDOM_STATE MAKE TRAINING PROCESS REPRODUCABLE,
# STARTIFY : SAME AMOUNT FROM EACH CATEGORY FOR THIS PROCESS, E.G. 60% SPORT AND 40% MEDIA ARE IN YOUR DATASET, SPLITTING PROCESS RESULTS BASED ON TEST_SIZE 0.6 PART WILL BE TAKEN FROM SPORT AND REMAINING FROM MEDIA. 
# ── Pipeline ──────────────────────────────────────────────────────────────────
pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(
        stop_words=None,          # Uzbek stop-words not built-in; keep all tokens
        ngram_range=(1, 2),       # CHARACTER BASED TOKENIZING AND DECIDING HOW MANY BLOCKS GONNA BE THERE
        max_features=10000,       # MOST USED 10K BLOCKS
        analyzer="word",          # character n-grams work better for morphologically rich Uzbek
        min_df=1,                 # KEEPING WORDS MIN FREQUENCY IS 1
    )),
    ("nb", MultinomialNB(alpha=0.5)), # USING MULTINOMIAL NAIVE BASED ALGORITM WITH 0.5 ALPHA TO KEEP TRACK OF NOT SEEN UNITS IN TRAINING PROCESS.
])

pipeline.fit(X_train, y_train)

# ── Evaluation ────────────────────────────────────────────────────────────────
y_pred = pipeline.predict(X_test)
print("=== Test set report ===")
print(classification_report(y_test, y_pred))

train_acc = pipeline.score(X_train, y_train) * 100
test_acc  = pipeline.score(X_test,  y_test)  * 100
print(f"Train accuracy : {train_acc:.1f}%")
print(f"Test  accuracy : {test_acc:.1f}%")

# ── Save ──────────────────────────────────────────────────────────────────────
dump(pipeline, "uzbek_gov_classifier.skops")

print("\nModel saved as uzbek_gov_classifier.skops")


with open("uzbek_gov_classifier.skops", "rb") as f:
    raw = f.read()
# Step 1: inspect what types are inside before trusting
unknown_types = get_untrusted_types(data=raw)
print("Types found in model file:", unknown_types)

# Step 2: explicitly approve and load
pipeline = loads(raw, trusted=unknown_types)

# ── Quick demo ────────────────────────────────────────────────────────────────
samples = [
    "Pasportimni yo'qotdim.",
    "Soliq to'lash muddatini o'tkazib yubordim.",
    "Shifokor noto'g'ri dori yozdi.",
    "Mansabdor shaxs korrupsiya qildi.",
    "Nikoh guvohnomamni yangilashim kerak.",
]

print("\n=== Demo predictions ===")
for s in samples:
    print(f"  '{s}'\n    → {pipeline.predict([s])[0]}\n")