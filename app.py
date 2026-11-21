"""Medical insurance charges predictor (XGBoost) - Streamlit app.

Model: XGBRegressor trained on 6 features, in this exact order:
    age, sex, bmi, children, smoker, region
Categorical encoding the model was trained with (alphabetical / LabelEncoder):
    sex    : female=0, male=1
    smoker : no=0,     yes=1
    region : northeast=0, northwest=1, southeast=2, southwest=3
"""
import os
import pickle

import pandas as pd
import streamlit as st

MODEL_PATH = os.environ.get("MODEL_PATH", "xgboost.pkl")

FEATURES = ["age", "sex", "bmi", "children", "smoker", "region"]
SEX_MAP = {"female": 0, "male": 1}
SMOKER_MAP = {"no": 0, "yes": 1}
REGION_MAP = {"northeast": 0, "northwest": 1, "southeast": 2, "southwest": 3}

st.set_page_config(page_title="Insurance Charges Predictor", page_icon="💰")


@st.cache_resource
def load_model(path: str):
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Model file '{path}' not found. Put your .pkl next to app.py "
            "and name it 'xgboost.pkl' (or set the MODEL_PATH env variable)."
        )
    with open(path, "rb") as f:
        return pickle.load(f)


st.title("💰 Medical Insurance Charges Predictor")
st.caption("XGBoost regression model - enter the details and get the estimated yearly charges.")

try:
    model = load_model(MODEL_PATH)
except Exception as e:  # show a readable error instead of a stack trace
    st.error(f"Could not load model: {e}")
    st.stop()

col1, col2 = st.columns(2)
with col1:
    age = st.number_input("Age", min_value=18, max_value=100, value=30, step=1)
    bmi = st.number_input("BMI", min_value=10.0, max_value=60.0, value=25.0, step=0.1, format="%.1f")
    children = st.number_input("Number of children", min_value=0, max_value=10, value=0, step=1)
with col2:
    sex = st.selectbox("Sex", list(SEX_MAP.keys()))
    smoker = st.selectbox("Smoker", list(SMOKER_MAP.keys()))
    region = st.selectbox("Region", list(REGION_MAP.keys()))

if st.button("Predict charges", type="primary"):
    X = pd.DataFrame(
        [[age, SEX_MAP[sex], bmi, children, SMOKER_MAP[smoker], REGION_MAP[region]]],
        columns=FEATURES,
    ).astype({"age": "int64", "sex": "int64", "bmi": "float64",
              "children": "int64", "smoker": "int64", "region": "int64"})
    pred = float(model.predict(X)[0])
    st.success(f"Estimated insurance charges: **${max(pred, 0):,.2f}**")
    with st.expander("Model input"):
        st.dataframe(X)
