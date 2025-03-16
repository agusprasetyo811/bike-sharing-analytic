import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import scipy.stats as stats
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
sns.set(style='dark')
import altair as alt

# Inisialisasi session state untuk navigasi
if "page" not in st.session_state:
    st.session_state["page"] = "Home"

# Fungsi untuk mengganti halaman
def change_page(page):
    st.session_state["page"] = page

# Membaca Dataset
days_df = pd.read_csv("day.csv")
hours_df = pd.read_csv("hour.csv")
days_df["cnt_log"] = np.log1p(days_df["cnt"])


# st.header('Bike Sharing Dashboard')

st.sidebar.title("Bike Sharing")
page = st.sidebar.radio(
	"Laporan Pengguna Sepeda", [
    "Halaman Utama",
    "Ringkasan",
		"Pengaruh Musim", 
		"Pengaruh Cuaca",
    "Hari Kerja vs Libur",
    "Trend Bulanan",
    "Trend Pengguna per Jam",
    "Casual vs Registered User",
    "Analisis Lanjutan"
	]
)

# Set tailwind style
tailwind_cdn = """
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
"""
st.markdown(tailwind_cdn, unsafe_allow_html=True)

# Filter
st.sidebar.header("Filter")

# Fungsi checkbox filter
def create_checkbox_filter(title, filter_dict):
    st.sidebar.write(f"### {title}")
    filter_df = pd.DataFrame(filter_dict)
    selected_values = [row["value"] for _, row in filter_df.iterrows() if st.sidebar.checkbox(row["key"], value=True)]
    return selected_values

# Filter by Year
year_filter = {
    'key': ["2011", "2012"],
    'value': [0, 1]
}
year_filter_df = pd.DataFrame(year_filter)
selected_years = st.sidebar.multiselect("Pilih Tahun", year_filter_df['key'].tolist(), default=year_filter_df['key'].tolist())
selected_year_values = year_filter_df[year_filter_df['key'].isin(selected_years)]['value'].tolist()

# Filter by Month
month_filter = {
    'key': ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
            "Jul", "Aug", "Sept", "Okt", "Nov", "Des"],
    'value': list(range(1, 13))
}
month_filter_df = pd.DataFrame(month_filter)
selected_months = st.sidebar.multiselect("Pilih Bulan", month_filter_df['key'].tolist(), default=month_filter_df['key'].tolist())
selected_month_values = month_filter_df[month_filter_df['key'].isin(selected_months)]['value'].tolist()

# Filter by Season
season_filter = {
    'key': ["Spring", "Summer", "Fall", "Winter"],
    'value': [1, 2, 3, 4]
}
selected_seasons = create_checkbox_filter("Filter Season", season_filter)

# Filter by Weathersit
weathersit_filter = {
    'key': ["Clear", "Mist", "Light Snow", "Heavy Rain"],
    'value': [1, 2, 3, 4]
}
selected_weathersit = create_checkbox_filter("Filter Weathersit", weathersit_filter)

# Filter by Workingday
workingday_filter = {
    'key': ["Hari Kerja", "Hari Libur"],
    'value': [1, 0]
}
selected_workingdays = create_checkbox_filter("Filter Workingday", workingday_filter)


# Filter DataFrame 
filtered_df = days_df.copy()
filtered_hours_df = hours_df.copy()

if selected_year_values:
  filtered_df = filtered_df[filtered_df["yr"].isin(selected_year_values)]
  filtered_hours_df = filtered_hours_df[filtered_hours_df["yr"].isin(selected_year_values)]
if selected_seasons:
	filtered_df = filtered_df[filtered_df["season"].isin(selected_seasons)]	
	filtered_hours_df = filtered_hours_df[filtered_hours_df["season"].isin(selected_seasons)]	
if selected_weathersit:
	filtered_df = filtered_df[filtered_df["weathersit"].isin(selected_weathersit)]
	filtered_hours_df = filtered_hours_df[filtered_hours_df["weathersit"].isin(selected_seasons)]	
if selected_workingdays:
	filtered_df = filtered_df[filtered_df["workingday"].isin(selected_workingdays)]
	filtered_hours_df = filtered_hours_df[filtered_hours_df["workingday"].isin(selected_workingdays)]
if selected_month_values:
	filtered_df = filtered_df[filtered_df["mnth"].isin(selected_month_values)]
	filtered_hours_df = filtered_hours_df[filtered_hours_df["mnth"].isin(selected_month_values)]

if page == "Halaman Utama":
  st.title("Bike Sharing")
  st.write("Selamat datang di dashboard Bike Sharing!")
  st.markdown(
    "Dalam dashboard akan dilakukan analisis terhadap laporan penggunaan sepeda mulai dari beberapa kategori seperti\n"
    "- Pengaruh Musim terhadap jumlah pengguna sepeda\n"
    "- Pengaruh Cuaca terhadap jumlah pengguna sepeda\n"
    "- Perbandingan jumlah pengguna di hari kerja dan hari libur\n"
    "- Trend bulanan dari aktivitas pengguna sepeda\n"
    "- Trend Pengguna per jam\n"
    "- Perbandingan Casual vs Registered User\n\n"
    "Pilih menu disamping untuk melihat hasil laporan"
  )
elif page == "Ringkasan":
  st.title("Ringkasan")
    
  total_cnt = filtered_df["cnt"].sum()
  formatted_total_cnt = f"{total_cnt:,}"
  avg_cnt = filtered_df["cnt"].mean()
  formatted_avg_cnt = f"{avg_cnt:,.2f}"
  total_casual = filtered_df["casual"].sum()
  formatted_total_casual = f"{total_casual:,}"
  total_registered = filtered_df["registered"].sum()
  formatted_total_registered = f"{total_registered:,}"
  
  columns = st.columns(2)
  with columns[0]:
    st.markdown(f"""
        <div class="bg-white border shadow-sm rounded-xl p-4">
          <p class="text-sm">Total Pengguna Sepeda</p>
          <h2 class="text-lg">{formatted_total_cnt}</h2>
        </div>
        """, 
      unsafe_allow_html=True
    )
  with columns[1]:
    st.markdown(f"""
        <div class="bg-white border shadow-sm rounded-xl p-4">
          <p class="text-sm">Rata-rata Pengguna Sepeda</p>
          <h2 class="text-lg">{formatted_avg_cnt}</h2>
        </div>
        """, 
      unsafe_allow_html=True
    )
  
  st.markdown(f"""
			<div class="mb-3"></div>
  	""",
 		unsafe_allow_html=True
  )
    
  columns = st.columns(2)
  with columns[0]:
    st.markdown(f"""
        <div class="bg-white border shadow-sm rounded-xl p-4">
          <p class="text-sm">Total Pengguna Casual</p>
          <h2 class="text-lg">{formatted_total_casual}</h2>
        </div>
        """, 
      unsafe_allow_html=True
    )
  with columns[1]:
    st.markdown(f"""
        <div class="bg-white border shadow-sm rounded-xl p-4">
          <p class="text-sm">Total Pengguna Registered</p>
          <h2 class="text-lg">{formatted_total_registered}</h2>
        </div>
        """, 
      unsafe_allow_html=True
    )
  
  st.markdown(f"""
			<div class="mb-10"></div>
  	""",
 		unsafe_allow_html=True
  )
  
  # Visualisasi Perbandingan Casual vs Register
  st.write("### Perbandingan Pengguna Casual dan Registered")
  chart_data = pd.DataFrame({
			"Kategori": ["Casual", "Registered"],
			"Jumlah Pengguna": [total_casual, total_registered]
	})
  chart = alt.Chart(chart_data).mark_bar().encode(
			x=alt.X("Kategori", sort=None),
			y="Jumlah Pengguna",
			color="Kategori"
	).properties(
			width=600,
			height=400
	)
  st.altair_chart(chart, use_container_width=True)
  
  # Visualisasi Tren perbulan
  monthly_trend = filtered_df.groupby("mnth")[["casual", "registered"]].sum().reset_index()
  month_map = {
			1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "Mei", 6: "Jun",
			7: "Jul", 8: "Aug", 9: "Sept", 10: "Okt", 11: "Nov", 12: "Des"
	}
  monthly_trend["mnth_label"] = monthly_trend["mnth"].map(month_map)
  monthly_trend_melted = monthly_trend.melt(
    id_vars=["mnth", "mnth_label"], 
    value_vars=["casual", "registered"], 
		var_name="Kategori Pengguna", 
		value_name="Jumlah Pengguna"
  )
  monthly_trend_melted = monthly_trend_melted.sort_values(by="mnth")
  st.write("### Tren Jumlah Pengguna (Casual & Registered) per bulan")
  chart = alt.Chart(monthly_trend_melted).mark_line(point=True).encode(
			x=alt.X("mnth_label:N", title="Bulan", sort=list(month_map.values())),
			y=alt.Y("Jumlah Pengguna:Q", title="Jumlah Pengguna"),
			color="Kategori Pengguna:N",
			tooltip=["mnth_label", "Kategori Pengguna", "Jumlah Pengguna"]
	).properties(
			width=800,
			height=400
	)
  st.altair_chart(chart, use_container_width=True)
  
  # Visualisasi Tren Season
  season_trend = filtered_df.groupby("season")[["casual", "registered"]].sum().reset_index()
  season_map = {
    1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"
	}
  season_trend["season_label"] = season_trend["season"].map(season_map)
  season_trend_melted = season_trend.melt(
    id_vars=["season", "season_label"], 
		value_vars=["casual", "registered"], 
		var_name="Kategori Pengguna", 
		value_name="Jumlah Pengguna"
  )
  season_trend_melted = season_trend_melted.sort_values(by="season")
  st.write("### Tren Jumlah Pengguna (Casual & Registered) per Musim")
  chart = alt.Chart(season_trend_melted).mark_bar().encode(
			x=alt.X("season_label:N", title="Musim", sort=["Spring", "Summer", "Fall", "Winter"]),
			y=alt.Y("Jumlah Pengguna:Q", title="Jumlah Pengguna"),
			color="Kategori Pengguna:N",
			tooltip=["season_label", "Kategori Pengguna", "Jumlah Pengguna"]
	).properties(
			width=800,
			height=400
	)
  st.altair_chart(chart, use_container_width=True)
  
  # Visualisasi weathersit 
  weathersit_trend = filtered_df.groupby("weathersit")[["casual", "registered"]].sum().reset_index()
  weathersit_map = {
			1: "Clear",
			2: "Mist",
			3: "Light Snow",
			4: "Heavy Rain"
	}
  weathersit_trend["weathersit_label"] = weathersit_trend["weathersit"].map(weathersit_map)
  weathersit_trend_melted = weathersit_trend.melt(
    id_vars=["weathersit", "weathersit_label"], 
		value_vars=["casual", "registered"], 
		var_name="Kategori Pengguna", 
		value_name="Jumlah Pengguna"
  )
  weathersit_trend_melted = weathersit_trend_melted.sort_values(by="weathersit")
  st.write("### Tren Jumlah Pengguna (Casual & Registered) berdasarkan Kondisi Cuaca")
  chart = alt.Chart(weathersit_trend_melted).mark_bar().encode(
			x=alt.X("weathersit_label:N", title="Kondisi Cuaca", sort=["Clear", "Mist", "Light Snow", "Heavy Rain"]),
			y=alt.Y("Jumlah Pengguna:Q", title="Jumlah Pengguna"),
			color="Kategori Pengguna:N",
			tooltip=["weathersit_label", "Kategori Pengguna", "Jumlah Pengguna"]
	).properties(
			width=800,
			height=400
	)
  st.altair_chart(chart, use_container_width=True)
  
  # Visualisasi Trend Workingday
  workingday_trend = filtered_df.groupby("workingday")[["casual", "registered"]].sum().reset_index()
  workingday_map = {
			1: "Hari Kerja",
			0: "Hari Libur"
	}
  workingday_trend["workingday_label"] = workingday_trend["workingday"].map(workingday_map)
  workingday_trend_melted = workingday_trend.melt(
   	id_vars=["workingday", "workingday_label"], 
		value_vars=["casual", "registered"], 
		var_name="Kategori Pengguna", 
		value_name="Jumlah Pengguna"
  )
  workingday_trend_melted = workingday_trend_melted.sort_values(by="workingday")
  st.write("### Tren Jumlah Pengguna (Casual & Registered) berdasarkan Hari Kerja")
  chart = alt.Chart(workingday_trend_melted).mark_bar().encode(
			x=alt.X("workingday_label:N", title="Hari", sort=["Hari Libur", "Hari Kerja"]),
			y=alt.Y("Jumlah Pengguna:Q", title="Jumlah Pengguna"),
			color="Kategori Pengguna:N",
			tooltip=["workingday_label", "Kategori Pengguna", "Jumlah Pengguna"]
	).properties(
			width=800,
			height=400
	)
  st.altair_chart(chart, use_container_width=True)
elif page == "Pengaruh Musim":
	st.title("Pengaruh Musim terhadap jumlah pengguna sepeda")
	
	# Transformasi days_df khusus untuk season
	season_labels = {
			1: "spring",
			2: "summer",
			3: "fall",
			4: "winter"
	}
	season_df = filtered_df.reset_index()
	season_df.season =  season_df.season.map(season_labels)
						
	st.markdown("---")
						
	st.write("##### Berdasarkan Hasil Analisis ")
	season_groups = [season_df[season_df["season"] == s]["cnt_log"] for s in season_df["season"].unique()]
	anova_result = stats.f_oneway(*season_groups)
	
	if anova_result.pvalue < 0.05:st.write("Terdapat perbedaan signifikan jumlah pengguna antar season.")
	else:st.write("Tidak ada perbedaan signifikan jumlah pengguna antar season.")
						
	st.markdown("---")
	
	# Menampilkan summary mean dalam table
	season_summary = season_df.groupby(by="season").agg({
		"cnt_log": "mean"                  
	}).rename(columns={"index":"Season", "cnt_log": "Rata-rata Pengguna"}).rename_axis("Season")
	st.write("##### Tabel perbandingan rata-rata pengguna berdasarkan season")
	st.dataframe(season_summary)

	# Visualisasi Season
	st.write("##### Grafik perbandingan rata-rata pengguna berdasarkan season") 
	fig, ax = plt.subplots(figsize=(35, 15))
	sns.barplot(x="season", y="cnt_log", data=season_df, color="skyblue", estimator=np.mean, ax=ax)
	ax.set_ylabel(None)
	ax.set_xlabel("Season", fontsize=30)
	ax.set_title("Rata-rata pengguna berdasarkan season", loc="center", fontsize=50, pad=30)
	ax.tick_params(axis='y', labelsize=35)
	ax.tick_params(axis='x', labelsize=30)
	st.pyplot(fig)
						
	# Menampikan Uji Anova
	st.write("##### Hasil uji statistik ANOVA")
	st.write(f"P-Value ANOVA: {anova_result.pvalue}")

	# Uji Statistic Post-Hoc Test dan tampilakan dalam bentuk table
	season_tukey = pairwise_tukeyhsd(season_df["cnt_log"], season_df["season"])
	season_tukey_df = pd.DataFrame(data=season_tukey.summary().data[1:], columns=season_tukey.summary().data[0])
	st.write("##### Tabel perbandingan hasil tukey HSD Test")
	st.dataframe(season_tukey_df)

	st.write(
		"Setelah dilakukan Uji ANOVA ternyata terdapat perbedaan yang signifikan bahwa season mempengaruhi jumlah pengguna.\n"
		"Detail perbedaan yang signifikan terlihat jelas pada uji Post-Hoc Test dimana  p-aj rata-rata dibawah < 0.05 dan nilai reject true"
	)   
elif page == "Pengaruh Cuaca":
	st.title("Pengaruh Cuaca terhadap jumlah pengguna sepeda")
	
	# Transformasi days_df khusus untuk season
	weathersit_labels = {
			1: "Clear",
			2: "Mist",
			3: "Light Snow",
			4: "Heavy Rain"
	}
	weathersit_df = filtered_df.reset_index()
	weathersit_df.weathersit =  weathersit_df.weathersit.map(weathersit_labels)
						
	st.markdown("---")
	st.write("##### Berdasarkan Hasil Analisis ")
	group1 = weathersit_df[weathersit_df["weathersit"] == 'Clear']["cnt_log"]
	group2 = weathersit_df[weathersit_df["weathersit"] == 'Mist']["cnt_log"]
	group3 = weathersit_df[weathersit_df["weathersit"] == 'Light Snow']["cnt_log"]
	group4 = weathersit_df[weathersit_df["weathersit"] == 'Heavy Rain']["cnt_log"]

	# Uji ANOVA
	f_stat, p_value = stats.f_oneway(group1, group2, group3)
	
	if p_value < 0.05:st.write("Hasil signifikan: Cuaca berpengaruh terhadap jumlah pengguna sepeda.")
	else:st.write("Hasil tidak signifikan: Cuaca mungkin tidak memiliki pengaruh yang besar.")
	st.markdown("---")
	
	st.write("##### Grafik persebaran dampak cuaca terhadap pengguna sepeda")
	fig, ax = plt.subplots(figsize=(35, 15))
	sns.boxplot(x="weathersit", hue="weathersit", y="cnt_log", data=weathersit_df, palette="Set2", ax=ax)
	ax.set_ylabel("Log Jumlah Pengguna Sepeda", fontsize=30)
	ax.set_xlabel("Weathersit (Cuaca)", fontsize=30)
	ax.set_title("Dampak Cuaca terhadap Jumlah Pengguna Sepeda", loc="center", fontsize=50, pad=30)
	ax.tick_params(axis='y', labelsize=35)
	ax.tick_params(axis='x', labelsize=30)
	st.pyplot(fig)
	
	# Menampikan Uji Anova
	st.write("##### Hasil uji statistik ANOVA")
	st.write(f"F-statistic: {f_stat:.4f}, p-value: {p_value:.4f}")
							
	# Uji Statistic Post-Hoc Test dan tampilakan dalam bentuk table
	weathersit_tukey = pairwise_tukeyhsd(endog=weathersit_df["cnt_log"], groups=weathersit_df["weathersit"], alpha=0.05)
	weathersit_tukey_df = pd.DataFrame(data=weathersit_tukey.summary().data[1:], columns=weathersit_tukey.summary().data[0])
	st.write("##### Tabel perbandingan hasil tukey HSD Test")
	st.dataframe(weathersit_tukey_df)
							
	# Visualisasi weathersit tukey
	group1 = weathersit_tukey_df["group1"].astype(str)
	group2 = weathersit_tukey_df["group2"].astype(str)
	mean_diff = weathersit_tukey_df["meandiff"]
	p_values = weathersit_tukey_df["p-adj"]
	colors = ["red" if p < 0.05 else "gray" for p in p_values]

	fig, ax = plt.subplots(figsize=(35, 15))
	ax.barh([f"{g1} vs {g2}" for g1, g2 in zip(group1, group2)], mean_diff, color=colors)
	ax.axvline(x=0, color="black", linestyle="--", linewidth=1)
	ax.set_ylabel("Perbandingan Weathersit", fontsize=30)
	ax.set_xlabel("Perbedaan Rata-rata (Meandiff)", fontsize=30)
	ax.set_title("Hasil Tukey HSD: Pengaruh Cuaca terhadap Pengguna Sepeda", loc="center", fontsize=50, pad=30)
	ax.tick_params(axis='y', labelsize=35)
	ax.tick_params(axis='x', labelsize=30)
	st.pyplot(fig)
							
	st.write(
		"Setelah dilakukan Uji ANOVA ternyata terdapat perbedaan yang signifikan bahwa weathersit mempengaruhi jumlah pengguna.\n"
		"Detail perbedaan yang signifikan terlihat jelas pada uji Post-Hoc Test dimana  p-aj rata-rata dibawah < 0.05 dan nilai reject true.\n"
		"Jika dilihat dari Tukey HSD terdapat perbedaan yang signifikan antar kedua kategori cuaca"
	)
elif page == "Hari Kerja vs Libur":
	st.title("Perbandingan jumlah pengguna di hari kerja dan hari libur")
	st.markdown("---")
	st.write("##### Berdasarkan Hasil Analisis ")
	st.write("Jumlah pengguna sepeda pada hari kerja dan hari biasa sangat dominan bila dibandingkan dengan hari libur / libur nasional")
	st.markdown("---")
	
	fig, ax = plt.subplots(figsize=(35, 15))
	
	sns.histplot(filtered_df[filtered_df['workingday'] == 1]['cnt_log'], kde=True, color='blue', label='Hari Kerja', bins=30, alpha=0.6, ax=ax)
	sns.histplot(filtered_df[filtered_df['workingday'] == 0]['cnt_log'], kde=True, color='red', label='Hari Libur', bins=30, alpha=0.6, ax=ax)
	ax.set_ylabel("Frekuensi", fontsize=30)
	ax.set_xlabel("Jumlah Pengguna Sepeda", fontsize=30)
	ax.set_title("Distribusi Pengguna Sepeda: Hari Kerja vs Hari Libur", loc="center", fontsize=50, pad=30)
	ax.tick_params(axis='y', labelsize=35)
	ax.tick_params(axis='x', labelsize=30)
	ax.legend(title="", fontsize=30, title_fontsize=30, loc="upper left")
	st.pyplot(fig)
	
	fig, ax = plt.subplots(figsize=(35, 15))
	sns.histplot(filtered_df[filtered_df['holiday'] == 1]['cnt_log'], kde=True, color='blue', label='Hari Libur Nasional', bins=30, alpha=0.6, ax=ax)
	sns.histplot(filtered_df[filtered_df['holiday'] == 0]['cnt_log'], kde=True, color='red', label='Hari Biasa', bins=30, alpha=0.6, ax=ax)
	ax.set_ylabel("Frekuensi", fontsize=30)
	ax.set_xlabel("Jumlah Pengguna Sepeda", fontsize=30)
	ax.set_title("Distribusi Pengguna Sepeda: Hari Libur Nasional vs Hari Biasa", loc="center", fontsize=50, pad=30)
	ax.tick_params(axis='y', labelsize=35)
	ax.tick_params(axis='x', labelsize=30)
	ax.legend(title="", fontsize=30, title_fontsize=30, loc="upper left")
	st.pyplot(fig)
elif page == "Trend Bulanan":
	st.title("Trend bulanan dari aktivitas pengguna sepeda")
	st.markdown("---")
	st.write("##### Berdasarkan Hasil Analisis ")
	st.write("Pengguna meningkat dari awal tahun dan mencapai puncaknya pada bulan Mei - September")
	st.markdown("---")
							
	fig, ax = plt.subplots(figsize=(35, 15))
	monthly_trend = filtered_df.groupby("mnth")["cnt"].mean()
	ax.plot(monthly_trend.index, monthly_trend.values, marker='o', linestyle='-', color='b')
	ax.set_xticks(range(1, 13)) 
	ax.set_xticklabels([
		"Jan", "Feb", "Mar", "Apr", "May", "Jun", 
		"Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
	])
	ax.set_ylabel("Rata-rata Pengguna Harian", fontsize=30)
	ax.set_xlabel("Bulan", fontsize=30)
	ax.set_title("Tren Bulanan Penggunaan Sepeda", loc="center", fontsize=50, pad=30)
	ax.tick_params(axis='y', labelsize=35)
	ax.tick_params(axis='x', labelsize=30)
	st.pyplot(fig)              
elif page == "Trend Pengguna per Jam":
		st.title("Trend Pengguna per jam")
		st.markdown("---")
		st.write("##### Berdasarkan Hasil Analisis ")
		st.write("Trend Grafik menujukan beberapa pola seperti puncak pengguna terjadi di pagi dan sore hari dan pengguna rendah di malam dan dini hari")
		st.markdown("---")
                
		hourly_trend = filtered_hours_df.groupby("hr")["cnt"].mean()
                
		fig, ax = plt.subplots(figsize=(35, 15))
		ax.plot(hourly_trend.index, hourly_trend.values, marker='o', linestyle='-', color='b')
		ax.set_ylabel("Jumlah Rata-rata Pengguna", fontsize=30)
		ax.set_xlabel("Jam", fontsize=30)
		ax.set_title("Tren Pengguna Per Jam", loc="center", fontsize=50, pad=30)
		ax.tick_params(axis='y', labelsize=35)
		ax.tick_params(axis='x', labelsize=30)
		st.pyplot(fig)
elif page == "Casual vs Registered User":
	st.title("Perbandingan Casual vs Registered User")
	st.markdown("---")
	st.write("##### Berdasarkan Hasil Analisis ")
	st.write(
		"Pengguna casual lebih banyak diakhir pekan / hari libur dibanding hari kerja.\n"
  	"Pengguna registered lebih banyak di hari kerja.\n"
		"Pengguna casual lebih sensitif terhadap cuaca dibanding pengguna registered.\n"
		"Pada saat cuaca buruk pengguna registered lebih stabil.\n"
		"Jumlah pengguna casual meningkat pada suhu yang hangat dan cenderung turun pada suhu yang dingin dan kelembapan tinggi.\n"
		"Jumlah pengguna registered terlihat mengalami penurunan juga namun cenderung lebih stabil\n"
	)
	st.markdown("---")

	# Perbandingan casual & registered diambil dari mean workingday dan weathersit
	grouped_weekday = filtered_df.groupby("workingday")[["casual", "registered"]].mean()
	grouped_weather = filtered_df.groupby("weathersit")[["casual", "registered"]].mean()

	fig, ax = plt.subplots(figsize=(35, 15))
	sns.barplot(x=grouped_weekday.index, y=grouped_weekday["registered"], color="red", alpha=0.7, label="Registered", ax=ax)
	sns.barplot(x=grouped_weekday.index, y=grouped_weekday["casual"], color="blue", label="Casual", ax=ax)
	ax.set_xticks([0,1])
	ax.set_xticklabels(["Weekend/Holiday", "Weekday"])
	ax.set_ylabel("Rata-rata Jumlah Pengguna", fontsize=30)
	ax.set_xlabel("Kategori Hari", fontsize=30)
	ax.set_title("Perbandingan Pengguna Casual vs Registered pada Hari Kerja dan Akhir Pekan", loc="center", fontsize=50, pad=30)
	ax.tick_params(axis='y', labelsize=35)
	ax.tick_params(axis='x', labelsize=30)
	ax.legend(title="", fontsize=30, title_fontsize=30, loc="upper left")
	st.pyplot(fig) 
  
	fig, ax = plt.subplots(figsize=(35, 15))
	sns.barplot(x=grouped_weather.index, y=grouped_weather["registered"], color="red", alpha=0.7, label="Registered", ax=ax)
	sns.barplot(x=grouped_weather.index, y=grouped_weather["casual"], color="blue", label="Casual", ax=ax)
	ax.set_xticks([0,1,2])
	ax.set_xticklabels(["Cerah", "Mendung", "Hujan"])
	ax.set_ylabel("Rata-rata Jumlah Pengguna", fontsize=30)
	ax.set_xlabel("Kondisi Cuaca", fontsize=30)
	ax.set_title("Pengaruh Kondisi Cuaca terhadap Pengguna Casual vs Registered", loc="center", fontsize=50, pad=30)
	ax.tick_params(axis='y', labelsize=35)
	ax.tick_params(axis='x', labelsize=30)
	ax.legend(title="", fontsize=30, title_fontsize=30, loc="upper left")
	st.pyplot(fig)
	
	fig, ax = plt.subplots(figsize=(35, 15))
	sns.regplot(x=filtered_df["temp"], y=filtered_df["casual"], scatter_kws={"alpha":0.5}, label="Casual", color="blue", ax=ax)
	sns.regplot(x=filtered_df["temp"], y=filtered_df["registered"], scatter_kws={"alpha":0.5}, label="Registered", color="red", ax=ax)
	ax.set_ylabel("Temperatur (Normalisasi)", fontsize=30)
	ax.set_xlabel("Jumlah Pengguna", fontsize=30)
	ax.set_title("Pengaruh Suhu terhadap Pengguna Casual vs Registered", loc="center", fontsize=50, pad=30)
	ax.tick_params(axis='y', labelsize=35)
	ax.tick_params(axis='x', labelsize=30)
	ax.legend(title="", fontsize=30, title_fontsize=30, loc="upper left")
	st.pyplot(fig)
 
	fig, ax = plt.subplots(figsize=(35, 15))
	sns.regplot(x=filtered_df["hum"], y=filtered_df["casual"], scatter_kws={"alpha":0.5}, label="Casual", color="blue", ax=ax)
	sns.regplot(x=filtered_df["hum"], y=filtered_df["registered"], scatter_kws={"alpha":0.5}, label="Registered", color="red", ax=ax)
	ax.set_ylabel("Kelembaban (Normalisasi)", fontsize=30)
	ax.set_xlabel("Jumlah Pengguna", fontsize=30)
	ax.set_title("Pengaruh Kelembaban terhadap Pengguna Casual vs Registered", loc="center", fontsize=50, pad=30)
	ax.tick_params(axis='y', labelsize=35)
	ax.tick_params(axis='x', labelsize=30)
	ax.legend(title="", fontsize=30, title_fontsize=30, loc="upper left")
	st.pyplot(fig)
elif page == "Analisis Lanjutan":
  st.title("Analisis Lanjutan menggunakan metode Manual Grouping")
  st.markdown("---")
  st.write("##### Berdasarkan Hasil Analisis ")
  st.markdown("""
			<ul class="list-disc pl-5 text-gray-700">
					<li><b>Jumlah pengguna meningkat</b> selama bulan tertentu seperti <b>Juni-September</b>.</li>
					<li><b>Musim Panas (Summer) dan Musim Gugur (Fall)</b> mungkin memiliki lebih banyak pengguna karena <b>kondisi cuaca yang mendukung</b>.</li>
					<li>Pengguna casual lebih banyak di <b>akhir pekan / hari libur</b> dibanding hari kerja.</li>
					<li>Pengguna casual lebih sensitif terhadap cuaca dibanding pengguna registered</li>
     			<li>Pada saat cuaca buruk pengguna registered lebih stabil.</li>
			</ul>
			</ul>
		""",
 	unsafe_allow_html=True)
  st.markdown("""
			<div class="mb-4"></div>
		""", 
 	unsafe_allow_html=True)
  st.write("##### Strategi mengubah pengguna casual menjadi pengguna registered ")
  st.markdown(
		"- Targetkan promo kepada pengguna di cluster casual agar mereka lebih tertarik menjadi pengguna registered.\n"
		"- Berikan keuntungan eksklusif bagi pengguna registered seperti tarif lebih murah, akses jalur khusus, atau fitur tambahan.\n"
	)
  st.markdown("---")
  
  st.write("#### Jumlah pengguna per bulan dalam tiap tahun")
  monthly_trend = days_df.groupby(["yr", "mnth"])[["casual", "registered", "cnt"]].sum().reset_index()
  monthly_trend["yr"] = monthly_trend["yr"].map({0: "2011", 1: "2012"})
  monthly_trend["mnth"] = monthly_trend["mnth"].map({
    1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
    5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus",
    9: "September", 10: "Oktober", 11: "November", 12: "Desember"
	})
  
  sorted_by_cnt = monthly_trend.sort_values(by="cnt", ascending=False)
  sorted_by_casual = monthly_trend.sort_values(by="casual", ascending=False)
  sorted_by_registered = monthly_trend.sort_values(by="registered", ascending=False)
  
  st.write("##### Tabel jumlah semua pengguna per bulan dengan total tertinggi")
  st.dataframe(sorted_by_cnt)
  
  st.write("##### Tabel jumlah pengguna casual per bulan dengan total tertinggi")
  st.dataframe(sorted_by_casual)
 
  st.write("##### Tabel jumlah pengguna registered per bulan dengan total tertinggi")
  st.dataframe(sorted_by_registered)
  
  
  st.write("#### Rata-rata Jumlah Pengguna (Casual & Registered) per Musim (Season)")
  season_trend = days_df.groupby("season")[["casual", "registered", "cnt"]].mean().reset_index()
  season_trend["season"] = season_trend["season"].map({1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"})
  st.dataframe(season_trend)
  
  st.write("#### Rata-rata Jumlah Pengguna (Casual & Registered) dalam Cuaca (Weathersit)")
  weathersit_trend = days_df.groupby("weathersit")[["casual", "registered", "cnt"]].mean().reset_index()
  weathersit_trend["weathersit"] = weathersit_trend["weathersit"].map({1: "Clear", 2: "Mist", 3: "Light Snow", 4: "Heavy rain"})
  st.dataframe(weathersit_trend)

st.caption('Copyright (c) Agus Prasetyo')