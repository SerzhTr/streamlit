import streamlit as st
import pandas as pd
import numpy as np

st.title("Test case Genesis Accelerator")

df = pd.read_csv(r"Data_for_Python_ROMI.csv")
df = df.melt(id_vars = ["month", "media_source", "country_code","costs","total_users_in_cohort"], \
                       var_name="day_n", \
                       value_name="revenue").copy()
df['day_n'] = df['day_n'].apply(lambda x: int(x))


#Побудова ROMI поденно для кожного mediasource з можливістю фільтрації по країнах.

st.subheader("ROMI поденно для кожного mediasource з можливістю фільтрації по країнах")

#створюємо список країн для фільтру
country = (pd.unique(df['country_code'])).tolist()

with st.sidebar:
    selected_countries = st.multiselect("Choose countries", country)

# якщо не обрана жодна країна, то romi буде обчислюватись по усім країнам для кожного mediasource
if len(selected_countries) == 0:
    selected_countries = country

#фільтруємо датасет по обраним країнам, фільтрація не діє для Google Ads
res1 = df.query('country_code in @selected_countries or media_source == "Google Ads"')

#
t = res1.groupby(['media_source','day_n'])\
    .agg({'costs':'sum', 'revenue':'sum'})\
    .reset_index().copy()

t['romi'] = np.round(((t['revenue'] - t['costs'])/t['costs'])*100,2)
print(t)

st.line_chart(data = t, x='day_n', y = 'romi', color = 'media_source')

#Побудова ROMI поденно у розрізі топ-10 країн (топ вибираємо по витратах (cost) на маркетинг за весь час)

st.subheader("ROMI поденно у розрізі топ-10 країн (топ вибираємо по витратах (cost) на маркетинг за весь час)")

#визначаємо топ 10 країн по витратам на маркетинг
top10_countries = df.query('country_code != "Unknown"') \
  .groupby('country_code')\
  .agg({'costs': 'sum'}) \
  .sort_values('costs', ascending = False).head(10).reset_index()\
  .country_code.tolist()

t1 = df.query('country_code in @top10_countries')\
     .groupby(['country_code', 'day_n']) \
     .agg({'costs':'sum', 'revenue':'sum'}).reset_index().copy()

t1['romi'] = np.round(((t1['revenue'] - t1['costs'])/t1['costs'])*100,2)

st.line_chart(data = t1, x='day_n', y = 'romi', color = 'country_code')

#Топ-10 комбінацій mediasource та country з найвищим ROMI для кожного календарного місяця

st.subheader("Топ-10 комбінацій mediasource та country з найвищим ROMI для кожного
календарного місяця")

#обираємо місяць
chosen_month = st.radio("Choose month: ", ("June 2020", "August 2020", "September 2020"))

#визначає номер місяця
def give_month(n_month):
    if n_month == "June 2020":
        return 7
    elif n_month == "August 2020":
        return 8
    else:
        return 9

#визначає кількість днів у календарному місяці
def give_num_of_days(n_month):
    if n_month in ("June 2020", "August 2020"):
        return '30'
    else:
        return '29'

month = give_month(chosen_month)
day_nums = give_num_of_days(chosen_month)

t2 = df.query('month == @month and day_n == 30 and country_code != "Unknown" and costs != 0')\
  .groupby(['media_source', 'country_code'])\
  .agg({'costs':'sum', 'revenue':'sum'}).reset_index().copy()

t2['romi'] = np.round(((t2['revenue'] - t2['costs'])/t2['costs'])*100,2)
t2['combination'] = t2['media_source'] + " " + t2['country_code']

st.bar_chart(t2.sort_values('romi', ascending=False).head(10), x="combination", y="romi")
