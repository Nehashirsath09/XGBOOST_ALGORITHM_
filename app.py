    .card h2{font-family:'Space Grotesk',sans-serif;margin:0 0 22px;font-size:20px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}.field label{display:block;color:#b8c5db;font-size:13px;margin:0 0 8px}.field input,.field select{width:100%;background:#0b1222;border:1px solid #293751;color:#f1f5ff;border-radius:12px;padding:13px 14px;font:inherit;outline:none}.field input:focus,.field select:focus{border-color:#7484ff;box-shadow:0 0 0 3px #7484ff20}.hint{font-size:11px;color:#73829c;margin-top:6px}
    .btn{width:100%;margin-top:22px;border:0;border-radius:13px;padding:15px;color:white;font-weight:700;font-size:15px;cursor:pointer;background:linear-gradient(100deg,#6978f6,#22b8e6);box-shadow:0 10px 28px #5568e844;transition:transform .15s}.btn:hover{transform:translateY(-2px)}
    .result{height:100%;display:flex;flex-direction:column;justify-content:center;min-height:310px}.result .mini{color:#92a2bf;font-size:13px}.price{font-family:'Space Grotesk',sans-serif;font-size:clamp(34px,4vw,48px);font-weight:700;margin:10px 0;color:#83e4ff;word-break:break-word}.resultbox{background:#0c1527;border:1px solid #263b56;padding:20px;border-radius:18px;margin-top:16px}.resultbox p{margin:0;color:#9eacc5;line-height:1.65;font-size:13px}.notice{color:#7889a6;font-size:12px;line-height:1.6;margin-top:22px}.error{background:#451c2c;border:1px solid #8d3957;color:#ffc3d4;border-radius:12px;padding:12px;margin-bottom:16px}
    @media(max-width:780px){.layout{grid-template-columns:1fr}.top{align-items:flex-start}.card{padding:20px}}@media(max-width:480px){.grid{grid-template-columns:1fr}.wrap{padding:26px 14px}}
  </style>
</head><body><div class="wrap">
  <div class="top"><div class="brand"><div class="logo">✦</div><span>InsureIQ</span></div><div class="tag">ML · XGBoost</div></div>
  <section class="hero"><div class="eyebrow">Smart estimate · Machine learning</div><h1>Insurance cost<br>predictor.</h1><p>Enter a few details to get an estimated insurance charge from your trained XGBoost model.</p></section>
  <div class="layout"><section class="card"><h2>Your details</h2>
    {% if error %}<div class="error">{{ error }}</div>{% endif %}
    <form method="POST"><div class="grid">
      <div class="field"><label for="age">Age</label><input id="age" name="age" type="number" min="1" max="100" required value="{{ values.get('age','') }}"></div>
      <div class="field"><label for="sex">Sex</label><select id="sex" name="sex" required><option value="" disabled {% if not values.get('sex') %}selected{% endif %}>Select</option><option value="female" {% if values.get('sex')=='female' %}selected{% endif %}>Female</option><option value="male" {% if values.get('sex')=='male' %}selected{% endif %}>Male</option></select></div>
      <div class="field"><label for="bmi">BMI</label><input id="bmi" name="bmi" type="number" min="1" max="100" step="0.1" required value="{{ values.get('bmi','') }}"><div class="hint">Enter the BMI value used by your dataset.</div></div>
      <div class="field"><label for="children">Children / dependents</label><input id="children" name="children" type="number" min="0" max="20" required value="{{ values.get('children','0') }}"></div>
      <div class="field"><label for="smoker">Smoker</label><select id="smoker" name="smoker" required><option value="" disabled {% if not values.get('smoker') %}selected{% endif %}>Select</option><option value="no" {% if values.get('smoker')=='no' %}selected{% endif %}>No</option><option value="yes" {% if values.get('smoker')=='yes' %}selected{% endif %}>Yes</option></select></div>
      <div class="field"><label for="region">Region</label><select id="region" name="region" required><option value="" disabled {% if not values.get('region') %}selected{% endif %}>Select region</option>{% for r in ['northeast','northwest','southeast','southwest'] %}<option value="{{r}}" {% if values.get('region')==r %}selected{% endif %}>{{r|capitalize}}</option>{% endfor %}</select></div>
    </div><button class="btn" type="submit">Calculate estimate →</button></form></section>
    <aside class="card result">{% if prediction is not none %}<div class="mini">Predicted insurance cost</div><div class="price">${{ "{:,.2f}".format(prediction) }}</div><div class="resultbox"><p>Your model's estimate based on the values entered. This is a demo prediction, not an actual quote.</p></div>{% else %}<div class="mini">Your prediction will appear here</div><h2 style="font-size:28px;margin:12px 0">Ready when you are.</h2><div class="resultbox"><p>Fill in the details on the left and click <b>Calculate estimate</b> to run the model.</p></div>{% endif %}<div class="notice">Demo only. This model may reflect limitations or biases in its training data. Encoding assumptions should match the dataset used to train it.</div></aside></div>
</div></body></html>'''

@app.route("/", methods=["GET", "POST"])
def home():
    prediction = None
    error = None
    values = request.form.to_dict() if request.method == "POST" else {}
    if request.method == "POST":
        try:
            age = int(values.get("age", ""))
            sex = values.get("sex", "")
            bmi = float(values.get("bmi", ""))
            children = int(values.get("children", "0"))
            smoker = values.get("smoker", "")
            region = values.get("region", "")
            if not (1 <= age <= 100 and 1 <= bmi <= 100 and 0 <= children <= 20):
                raise ValueError("Please enter values within the displayed ranges.")
            if sex not in ("female", "male") or smoker not in ("yes", "no") or region not in REGION_MAP:
                raise ValueError("Please select a valid option for each field.")
            row = pd.DataFrame([{
                "age": age,
                "sex": 0 if sex == "female" else 1,
                "bmi": bmi,
                "children": children,
                "smoker": 1 if smoker == "yes" else 0,
                "region": REGION_MAP[region],
            }], columns=["age", "sex", "bmi", "children", "smoker", "region"])
            prediction = float(model.predict(row)[0])
        except (ValueError, TypeError) as exc:
            error = str(exc) or "Please check your inputs and try again."
    return render_template_string(PAGE, prediction=prediction, error=error, values=values)



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
