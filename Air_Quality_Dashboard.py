import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import math


# Fungsi untuk DataFrame
def byStation_PM(df):
    return df.groupby(['station', 'year']).agg({
        'PM2.5': 'mean',
        'PM10': 'mean',
    }).reset_index().sort_values(['station', 'year'], ascending=[True, True])

def Distribution_of_Pollutants(df):
    return df.groupby(['station', 'year']).agg({
        'SO2': 'mean',
        'NO2': 'mean',
        'CO': 'mean',
        'O3': 'mean'
    })

def Correlation_0f_Wind_Direction_with_PM25(df):
    return df.groupby(['station', 'year']).agg({
        'PM2.5': 'mean',
        'wd': lambda x: x.mode()[0]
    }).reset_index()

def Correlation_0f_Wind_Direction_with_PM10(df):
    return df.groupby(['station', 'year']).agg({
        'PM10': 'mean',
        'wd': lambda x: x.mode()[0]
    }).reset_index()

# Load Dataset
df = pd.read_csv('All Data PRSA (Air Quality).csv')
df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')

# Komponen filter date time
min_date = df['datetime'].min().date()
max_date = df['datetime'].max().date()

with st.sidebar:
    st.image('pollution.png')

    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

df = df[(df['datetime'] >= pd.to_datetime(start_date)) &
        (df['datetime'] <= pd.to_datetime(end_date))]

# Menerapkan fungsi
byStation_PM = byStation_PM(df)
Distribution_of_Pollutants = Distribution_of_Pollutants(df)
Correlation_0f_Wind_Direction_with_PM25 = Correlation_0f_Wind_Direction_with_PM25(df)
Correlation_0f_Wind_Direction_with_PM10 = Correlation_0f_Wind_Direction_with_PM10(df)

st.markdown("<h1 style='text-align: center;'>Kualitas Udara di Beijing, Tiongkok</h1>", unsafe_allow_html=True)


# Station dengan Kualitas udara terbaik dan terburuk
col1, col2, col3 = st.columns([4, 3, 4])

with col1:
    top_station_name = byStation_PM['station'].iloc[0]
    st.metric('Daerah dengan PM 2.5 terbaik', value=top_station_name)

with col2:
    st.markdown(
        f"<h1 style='text-align: center; font-size: 18px;'>{int(byStation_PM['PM2.5'].iloc[0])}µg/m³|{int(byStation_PM['PM2.5'].iloc[-1])}µg/m³</h1>", 
        unsafe_allow_html=True
    )

with col3:
    top_station_name = byStation_PM['station'].iloc[-1]
    st.metric('Daerah dengan PM 2.5 terburuk', value=top_station_name)


# Indeks PM setiap provinsi per tahun
safe_limit_pm25 = 35
safe_limit_pm10 = 50

stations = byStation_PM['station'].unique()  # Gunakan 'station' dari dataframe

n_rows = math.ceil(len(stations) / 2)

fig, ax = plt.subplots(nrows=n_rows, ncols=2, figsize=(24, 8 * n_rows))

ax = ax.flatten()  # Flattening the axis array so it can be accessed easily with indices

for i, station in enumerate(stations):

    # Remove the line ax = ax[i] and directly access ax[i]
    station_data = byStation_PM[byStation_PM['station'] == station].reset_index().sort_values('year', ascending=True)

    years = station_data['year']
    x = range(len(years))
    width = 0.35

    max_PM25_perYear = station_data.loc[station_data['PM2.5'].idxmax(), 'year']
    max_PM10_perYear = station_data.loc[station_data['PM10'].idxmax(), 'year']

    pm25_bars = ax[i].bar([j - width/2 for j in x], station_data['PM2.5'], width, label='PM2.5', color='skyblue')
    pm10_bars = ax[i].bar([j + width/2 for j in x], station_data['PM10'], width, label='PM10', color='lightgreen')

    for j, year in enumerate(years):
        if year == max_PM25_perYear:
            pm25_bars[j].set_color('darkblue')
        if year == max_PM10_perYear:
            pm10_bars[j].set_color('darkgreen')

    ax[i].axhline(y=safe_limit_pm25, color='blue', linestyle='--', label='PM2.5 Safe Limit (35 µg/m³)')
    ax[i].axhline(y=safe_limit_pm10, color='green', linestyle='--', label='PM10 Safe Limit (50 µg/m³)')

    ax[i].set_title(f'PM Concentration at {station}', fontsize=15)
    ax[i].set_xlabel('Year', fontsize=15)
    ax[i].set_ylabel('Concentration (µg/m³)', fontsize=15)
    ax[i].legend(fontsize=10)

    for j, v in enumerate(station_data['PM2.5']):
        ax[i].text(j - width/2, v, f'{v:.1f}', ha='center', va='bottom', fontsize=10)
    for j, v in enumerate(station_data['PM10']):
        ax[i].text(j + width/2, v, f'{v:.1f}', ha='center', va='bottom', fontsize=10)

    ax[i].set_xticks(x)
    ax[i].set_xticklabels(years, rotation=45)

# Hapus axis yang kosong jika jumlah subplot lebih dari jumlah data
for j in range(i + 1, len(ax)):
    fig.delaxes(ax[j])

plt.tight_layout()
st.pyplot(fig)


st.subheader('Hubungan antara  arah angin dan PM 2.5 dan PM 10')
# Wind direction vs  PM25 and Pm10
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(24, 20))

# Plot untuk PM2.5
sns.scatterplot(data=Correlation_0f_Wind_Direction_with_PM25, x='PM2.5', y='station', hue='wd', size='wd', sizes=(20, 200), ax=ax1)
ax1.set_title('Hubungan antara Rata-rata PM2.5 dan Arah Angin per Kota')

# Menambahkan anotasi tahun untuk PM2.5
for idx, row in Correlation_0f_Wind_Direction_with_PM25.iterrows():
    ax1.annotate(str(row['year']), 
                 (row['PM2.5'], row['station']),
                 xytext=(5, 0),
                 textcoords='offset points',
                 fontsize=15,
                 alpha=0.7)

# Plot untuk PM10
sns.scatterplot(data=Correlation_0f_Wind_Direction_with_PM10, x='PM10', y='station', hue='wd', size='wd', sizes=(20, 200), ax=ax2)
ax2.set_title('Hubungan antara Rata-rata PM10 dan Arah Angin per Kota')

# Menambahkan anotasi tahun untuk PM10
for idx, row in Correlation_0f_Wind_Direction_with_PM10.iterrows():
    ax2.annotate(str(row['year']), 
                 (row['PM10'], row['station']),
                 xytext=(5, 0),
                 textcoords='offset points',
                 fontsize=15,
                 alpha=0.7)

# Mengatur legenda
handles, labels = ax2.get_legend_handles_labels()
fig.legend(handles, labels, title='Arah Angin', bbox_to_anchor=(1.05, 0.5), loc='center left')

# Menghapus legenda dari masing-masing subplot
ax1.get_legend().remove()
ax2.get_legend().remove()

# Menyesuaikan layout dan menampilkan plot
plt.tight_layout()
st.pyplot(fig)

st.subheader('Kandungan Polutan setiap provinsi per tahun')
# Indeks Polutan setiap provinsi per tahun
pollutants = ['SO2', 'NO2', 'CO', 'O3']

# Batas aman untuk tiap polutan dalam satuan µg/m³
safe_limits = {
    'SO2': 20,
    'NO2': 40,
    'CO': 4000,  # CO dikonversi ke µg/m³
    'O3': 100
}

# Menghitung jumlah baris yang dibutuhkan (setiap 2 polutan per baris)
num_rows = (len(pollutants) + 1) // 2  # Pembulatan ke atas

# Membuat subplots grid dengan 2 kolom
fig, axes = plt.subplots(num_rows, 2, figsize=(15, 5 * num_rows))

# Meratakan array axes menjadi 1D untuk memudahkan iterasi
axes = axes.flatten()

# Looping untuk setiap polutan dan plot data
for i, pollutant in enumerate(pollutants):
    ax = axes[i]
    
    # Menghitung rata-rata untuk tiap stasiun
    avg_data = Distribution_of_Pollutants.groupby('station')[pollutant].mean()
    
    # Menentukan warna batang berdasarkan batas aman
    colors = ['skyblue' if val <= safe_limits[pollutant] else 'red' for val in avg_data]
    
    # Plot data rata-rata untuk tiap polutan
    bars = ax.bar(avg_data.index, avg_data.values, color=colors)
    
    # Menambahkan garis batas aman
    safe_limit = safe_limits[pollutant]
    ax.axhline(safe_limit, color='green', linestyle='--', linewidth=2, label=f'Safe Limit ({safe_limit} µg/m³)')
    
    # Menambahkan judul, label sumbu, dan rotasi label x
    ax.set_title(f'Average {pollutant} per Station', fontsize=14)
    ax.set_xlabel('Station', fontsize=12)
    ax.set_ylabel(f'{pollutant} (µg/m³)', fontsize=12)
    ax.tick_params(axis='x', rotation=45)
    
    # Menambahkan nilai di atas setiap batang
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2., height, f'{height:.2f}', ha='center', va='bottom')
    
    # Menambahkan legend
    ax.legend()

# Menghapus subplot yang tidak digunakan (jika ada)
for j in range(i + 1, len(axes)):
    fig.delaxes(axes[j])

# Mengatur tata letak agar tidak ada elemen yang terpotong
plt.tight_layout()

# Menampilkan plot menggunakan Streamlit
st.pyplot(fig)







st.title("Peta Kualitas Udara di Beijing")
st.components.v1.html(open('folium_map_geospatial.html', 'r').read(), height=500)

