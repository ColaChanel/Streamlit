import streamlit as st
import pandas as pd
import numpy as np
import pickle
from sklearn.ensemble import RandomForestClassifier

st.write("""
# Приложение для предсказания пингвинов
Это приложение предсказывает вид **Пальмерского пингвина**!
Данные взяты из [palmerpenguins library](https://github.com/allisonhorst/palmerpenguins) in R by Allison Horst.
""")

st.sidebar.header('Пользовательский ввод данных')

st.sidebar.markdown("""
[Пример CSV файла ввода](https://raw.githubusercontent.com/dataprofessor/data/master/penguins_example.csv)
""")
dir = "classification_penguins/images/"
# Collects user input features into dataframe
uploaded_file = st.sidebar.file_uploader("загрузите ваш CSV файл, по примеру выше", type=["csv"])
if uploaded_file is not None:
    input_df = pd.read_csv(uploaded_file)
else:
    def user_input_features():
        island = st.sidebar.selectbox('Остров',('Biscoe','Dream','Torgersen'))
        sex = st.sidebar.selectbox('Пол',('мужской','женский'))
        bill_length_mm = st.sidebar.slider('Bill length (мм)', 32.1,59.6,43.9)
        bill_depth_mm = st.sidebar.slider('Bill depth (мм)', 13.1,21.5,17.2)
        flipper_length_mm = st.sidebar.slider('Длина ласты (мм)', 172.0,231.0,201.0)
        body_mass_g = st.sidebar.slider('Масса тела (г)', 2700.0,6300.0,4207.0)
        st.sidebar.image(f"{dir}image.png")
        if sex =="женский": 
            sex ="female"
        else: 
            sex ="male"
        data = {'island': island,
                'bill_length_mm': bill_length_mm,
                'bill_depth_mm': bill_depth_mm,
                'flipper_length_mm': flipper_length_mm,
                'body_mass_g': body_mass_g,
                'sex': sex}
        features = pd.DataFrame(data, index=[0])
        return features
    input_df = user_input_features()

# Combines user input features with entire penguins dataset
# This will be useful for the encoding phase
penguins_raw = pd.read_csv('classification_penguins/penguins_cleaned.csv')
penguins = penguins_raw.drop(columns=['species'])
df = pd.concat([input_df,penguins],axis=0)

# Encoding of ordinal features
# https://www.kaggle.com/pratik1120/penguin-dataset-eda-classification-and-clustering
encode = ['sex','island']
for col in encode:
    dummy = pd.get_dummies(df[col], prefix=col)
    df = pd.concat([df,dummy], axis=1)
    del df[col]
df = df[:1] # Selects only the first row (the user input data)

# Displays the user input features
st.subheader('Введенные пользователем параметры')

if uploaded_file is not None:
    st.write(df)
else:
    st.write('Ожидается CSV файл который будет загружен. Сейчас используются параметры введенные справа (показываются ниже).')
    st.write(df)

# Reads in saved classification model
load_clf = pickle.load(open('classification_penguins/penguins_clf.pkl', 'rb'))

# Apply model to make predictions
prediction = load_clf.predict(df)
prediction_proba = load_clf.predict_proba(df)


st.subheader('Предсказание')
penguins_species = np.array(['Adelie','Chinstrap','Gentoo'])
pred =penguins_species[prediction]
st.write(pred)
if pred == 'Adelie':
    st.image(f'{dir}adelie.png')
elif pred == f'{dir}Chinstrap':
    st.image(f'{dir}chinstrap.png')
else:
    st.image(f'{dir}gentoo.png')

st.subheader('Вероятность предсказания')
st.write(prediction_proba)