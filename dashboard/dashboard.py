import streamlit as st
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import chi2_contingency

# ==========================================
# 1. KONFIGURASI HALAMAN & LOAD DATA
# ==========================================
st.set_page_config(page_title="Dashboard Insight Finansial", layout="wide", initial_sidebar_state="expanded")

current_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(current_dir, 'urban_budget_allocation_dataset.csv')

@st.cache_data 
def load_data():
    try:
        return pd.read_csv(data_path)
    except FileNotFoundError:
        st.error(f"File urban_budget_allocation_dataset.csv tidak ditemukan di jalur: {data_path}.")
        st.stop()

df_raw = load_data()
df = df_raw.copy() 

# ==========================================
# 2. SIDEBAR
# ==========================================
st.sidebar.title("🛠️ Pengaturan Dashboard")
st.sidebar.write("Gunakan filter di bawah ini untuk mengeksplorasi data.")

# Filter Pendapatan (Income)
st.sidebar.markdown("### 💰 Filter Pendapatan")
min_income = float(df_raw['Income'].min())
max_income = float(df_raw['Income'].max())
selected_income = st.sidebar.slider(
    "Rentang Pendapatan:",
    min_value=min_income,
    max_value=max_income,
    value=(min_income, max_income),
    step=1000.0
)
df = df[(df['Income'] >= selected_income[0]) & (df['Income'] <= selected_income[1])]

# Filter Kategori Finansial
st.sidebar.markdown("### 📊 Filter Kategori Finansial")

level_options = df_raw['FinancialLevel'].unique()
selected_levels = st.sidebar.multiselect(
    "Tingkat Kesehatan Finansial:", 
    options=level_options, 
    default=level_options
)
df = df[df['FinancialLevel'].isin(selected_levels)]

status_options = df_raw['FinancialStatus'].unique()
selected_status = st.sidebar.multiselect(
    "Status Saldo (Surplus/Deficit):", 
    options=status_options, 
    default=status_options
)
df = df[df['FinancialStatus'].isin(selected_status)]

savings_options = df_raw['SavingsStatus'].unique()
selected_savings = st.sidebar.multiselect(
    "Status Tabungan:", 
    options=savings_options, 
    default=savings_options
)
df = df[df['SavingsStatus'].isin(selected_savings)]

st.sidebar.markdown("### ⚙️ Preferensi Tampilan")
show_raw_data = st.sidebar.checkbox("Tampilkan Tabel Dataset")

# ==========================================
# 3. KONTEN UTAMA DASHBOARD & KPI
# ==========================================
st.title("📊 Dashboard Insight Kesehatan Finansial")
st.markdown("Eksplorasi hasil analisis perilaku pengelolaan keuangan individu secara interaktif. Dashboard ini dirancang untuk membantu Anda menemukan pola tersembunyi terkait kepatuhan anggaran, kebiasaan menabung, serta tingkat kesehatan finansial melalui berbagai filter yang tersedia. Anda dapat menggunakan Insight yang dihasilkan untuk memahami tren pengeluaran dan merumuskan strategi keuangan yang lebih cerdas.")

if show_raw_data:
    st.subheader("Dataset (Berdasarkan Filter)")
    st.dataframe(df, use_container_width=True)

st.divider()

st.subheader("Ringkasan Metrik Utama")
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
with kpi1:
    st.metric(label="Total Individu (Sesuai Filter)", value=f"{len(df):,}")
with kpi2:
    surplus_count = len(df[df['FinancialStatus'] == 'Surplus'])
    st.metric(label="Total Individu Surplus", value=f"{surplus_count:,}")
with kpi3:
    healthy_count = len(df[df['FinancialLevel'] == 'Healthy'])
    st.metric(label="Total Financial 'Healthy'", value=f"{healthy_count:,}")
with kpi4:
    on_track_count = len(df[(df['BudgetAdherenceRatio'] >= 0.9) & (df['BudgetAdherenceRatio'] <= 1.1)])
    st.metric(label="Budget 'On Track'", value=f"{on_track_count:,}")
with kpi5:
    healthy_saving_count = len(df[df['SavingsStatus'] == 'Healthy Saving'])
    st.metric(label="Total Healthy Savings", value=f"{healthy_saving_count:,}")

st.divider()

# ==========================================
# 4. VISUALISASI MENGGUNAKAN TABS
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs(["Kepatuhan Anggaran (Budget)", "Status Tabungan (Savings)", "Kondisi Finansial Keseluruhan", "Analisis A/B Testing"])

with tab1:
    st.header("Analisis Kepatuhan Anggaran & Kategori Pengeluaran")
    col_a, col_b = st.columns(2)
    
    with col_a:
        # --- ERROR HANDLING: Cek apakah data kosong akibat filter ---
        if not df.empty:
            adherence_category = df['BudgetAdherenceRatio'].apply(
                lambda x: (
                    "Under Budget" if x < 0.9
                    else "On Track" if 0.9 <= x <= 1.1
                    else "Over Budget"
                )
            )
            
            # Tambahkan fillna(0) agar jika filter menghasilkan 0 orang di satu kategori, tidak menjadi NaN
            counts = adherence_category.value_counts().reindex(['Under Budget', 'On Track', 'Over Budget']).fillna(0)
            budget_summary = pd.DataFrame({'Jumlah': counts.values}, index=counts.index)
            
            max_value = budget_summary['Jumlah'].max()

            fig = plt.figure(figsize=(8,5))

            plt.bar(
                budget_summary.index,
                budget_summary['Jumlah'],
            )

            plt.title("Budget Adherence Distribution")
            plt.xlabel("Category")
            plt.ylabel("Number of Individuals")

            # Memastikan max_value bukan NaN untuk mencegah error batas sumbu
            max_ylim = max_value + 50 if pd.notna(max_value) else 50
            plt.ylim(0, max_ylim)

            plt.xticks(rotation=0)

            st.pyplot(fig)
            
            # Insights
            total_users = int(budget_summary['Jumlah'].sum())
            
            if total_users > 0:
                # Mencari kategori terbanyak dan persentasenya
                dominant_cat = budget_summary['Jumlah'].idxmax()
                dominant_count = int(budget_summary['Jumlah'].max())
                dominant_pct = (dominant_count / total_users) * 100
                
                # Menghitung persentase Over Budget
                over_budget_count = int(budget_summary.loc['Over Budget', 'Jumlah'])
                over_budget_pct = (over_budget_count / total_users) * 100
                
                # Menampilkan Insight UI di bawah grafik
                st.markdown("##### 💡 Insight Kepatuhan:")
                st.markdown(f"- Dari total **{total_users}** individu, mayoritas berada pada kategori **{dominant_cat}** sebanyak **{dominant_count}** orang ({dominant_pct:.1f}%).")
                
                if over_budget_pct > 50:
                    st.error(f"- **Peringatan:** Lebih dari setengah kelompok ini ({over_budget_pct:.1f}%) mengalami pembengkakan pengeluaran (**Over Budget**).")
                elif over_budget_pct == 0:
                    st.success("- **Sangat Baik!** Tidak ada individu yang melebihi batas anggaran (**Over Budget**) pada filter ini.")

        else:
            # --- TAMPILAN JIKA FILTER KOSONG ---
            st.warning("Silakan pilih minimal satu opsi pada filter di sidebar untuk menampilkan grafik distribusi anggaran.")
        
    with col_b:
        if not df.empty:
            kategori_list = ['Housing', 'Transportation', 'Food', 'Utilities', 'Entertainment', 'Savings']
            over_budget_data = []
            
            for cat in kategori_list:
                expense_col = 'Savings' if cat == 'Savings' else f'{cat}Expense'
                batas_budget = (df[f'{cat}Budget'] / 100) * df['Income'] 
                is_over = df[expense_col] > batas_budget
                over_budget_data.append({'Category': cat, 'OverBudgetCount': is_over.sum()})
                
            result = pd.DataFrame(over_budget_data)
            result = result.sort_values(by='OverBudgetCount', ascending=False).reset_index(drop=True)
            
            if result['OverBudgetCount'].sum() > 0:
                max_value = result['OverBudgetCount'].max()

                colors = [
                    'crimson' if value == max_value else 'steelblue'
                    for value in result['OverBudgetCount']
                ]

                fig = plt.figure(figsize=(8,5))

                plt.bar(
                    result['Category'],
                    result['OverBudgetCount'],
                    color=colors
                )

                plt.title("Most Frequent Over Budget Categories")
                plt.xlabel("Expense Category")
                plt.ylabel("Frequency")

                plt.xticks(rotation=0)

                st.pyplot(fig)
                
                # Insight
                # Mengambil data posisi pertama (kategori paling sering Over Budget)
                top_category = result.iloc[0]['Category']
                top_count = int(result.iloc[0]['OverBudgetCount'])
                
                # Menghitung persentase dari total pengguna yang sedang difilter
                total_filtered_users = len(df)
                top_pct = (top_count / total_filtered_users) * 100 if total_filtered_users > 0 else 0
                
                st.markdown("##### 💡 Insight Kategori:")
                st.markdown(f"- Kebocoran anggaran paling tinggi terjadi pada kategori **{top_category}**, dengan **{top_count}** insiden Over Budget.")
                
                # Menampilkan posisi kedua jika ada nilainya
                if len(result) > 1 and result.iloc[1]['OverBudgetCount'] > 0:
                    second_cat = result.iloc[1]['Category']
                    second_count = int(result.iloc[1]['OverBudgetCount'])
                    st.markdown(f"- Posisi kedua ditempati oleh **{second_cat}** yang menyumbang **{second_count}** insiden.")

                # Logika Peringatan: Hanya muncul jika kondisinya parah (> 30%)
                if top_pct > 30:
                    st.error(f"- **Peringatan:** Tingkat kepatuhan rendah! Sebanyak **{top_pct:.1f}%** individu dalam filter ini gagal mengontrol pengeluaran **{top_category}** mereka.")

            else:
                st.info("Berdasarkan filter saat ini, tidak ada pengguna yang melebihi batas anggaran (Over Budget).")
        else:
            # --- TAMPILAN JIKA FILTER KOSONG ---
            st.warning("Data tidak tersedia. Sesuaikan filter untuk melihat kategori pengeluaran.")

with tab2:
    st.header("Analisis Kebiasaan Menabung")
    
    savings_summary = df['SavingsStatus'].value_counts().reset_index()
    savings_summary.columns = ['Savings Status', 'Jumlah Individu']
    
    if not savings_summary.empty:
        total_savings = savings_summary['Jumlah Individu'].sum()
        max_val3 = savings_summary['Jumlah Individu'].max()
        colors3 = ['#e63946' if val == max_val3 else '#3a86c8' for val in savings_summary['Jumlah Individu']]
        
        fig3, ax3 = plt.subplots(figsize=(4.5, 4))
        bars3 = ax3.bar(savings_summary['Savings Status'], savings_summary['Jumlah Individu'], color=colors3)
        
        for i, bar in enumerate(bars3):
            yval = bar.get_height()
            pct = (yval / total_savings) * 100
            ax3.text(bar.get_x() + bar.get_width()/2, yval + (max_val3*0.02), f'{pct:.2f}%', ha='center')
            
        ax3.set_title("Savings Status Distribution")
        ax3.set_xlabel("Savings Status")
        ax3.set_ylabel("Number of Individuals")
        ax3.set_ylim(0, max_val3 * 1.15)
        
        col_left, col_center, col_right = st.columns([1, 2, 1])
        
        with col_center:
            st.pyplot(fig3, use_container_width=False)
            
        # Insight
        # Mengambil data dominan (paling banyak)
        dominant_idx = savings_summary['Jumlah Individu'].idxmax()
        dominant_cat = savings_summary.loc[dominant_idx, 'Savings Status']
        dominant_count = savings_summary.loc[dominant_idx, 'Jumlah Individu']
        dominant_pct = (dominant_count / total_savings) * 100
        
        st.markdown("##### 💡 Insight Tabungan:")
        st.markdown(f"- Mayoritas individu (**{dominant_pct:.2f}%**) memiliki status tabungan **{dominant_cat}** dengan total **{dominant_count}** orang.")
        
        # Mengambil data minoritas (paling sedikit) jika ada lebih dari 1 kategori
        if len(savings_summary) > 1:
            lowest_idx = savings_summary['Jumlah Individu'].idxmin()
            lowest_cat = savings_summary.loc[lowest_idx, 'Savings Status']
            lowest_count = savings_summary.loc[lowest_idx, 'Jumlah Individu']
            lowest_pct = (lowest_count / total_savings) * 100
            
            st.markdown(f"- Sebaliknya, kelompok terkecil berada pada status **{lowest_cat}** yang hanya mencakup **{lowest_count}** orang ({lowest_pct:.2f}%).")
            
    else:
        # --- TAMPILAN JIKA FILTER KOSONG ---
        st.warning("Tidak ada data tabungan yang sesuai dengan filter.")

with tab3:
    st.header("Tingkat Kesehatan & Status Finansial")
    
    col_c, col_d = st.columns(2, gap="large") 
    
    with col_c:
        level_counts = df['FinancialLevel'].value_counts()
        if not level_counts.empty:
            colors4 = ['#3a86c8', '#708090', '#5f9ea0'] 
            
            fig4, ax4 = plt.subplots(figsize=(5, 3.5))
            
            ax4.set_position([0.1, 0.15, 0.8, 0.75])
            
            wedges, texts, autotexts = ax4.pie(
                level_counts, 
                autopct='%1.2f%%', 
                colors=colors4[:len(level_counts)], 
                wedgeprops={'width': 0.7} 
            )
            
            ax4.set_title("Distribution of Financial Levels", pad=5)
            
            ax4.legend(
                wedges, 
                level_counts.index, 
                loc="upper center", 
                bbox_to_anchor=(0.5, -0.02), 
                ncol=3, 
                frameon=False
            )
            
            st.pyplot(fig4, bbox_inches=None)
            
            # Insight
            total_levels = int(level_counts.sum())
            
            if total_levels > 0:
                # Mengambil data posisi pertama (kategori dominan)
                dominant_level = level_counts.index[0]
                dominant_count = int(level_counts.iloc[0])
                dominant_pct = (dominant_count / total_levels) * 100
                
                st.markdown("##### 💡 Insight Kesehatan:")
                st.markdown(f"- Mayoritas individu pada filter ini berada di tingkat **{dominant_level}** dengan jumlah **{dominant_count}** orang ({dominant_pct:.2f}%).")
                
                # Menampilkan data pertengahan (Unhealthy) jika ada 3 kategori penuh
                if len(level_counts) == 3:
                    middle_level = level_counts.index[1]
                    middle_count = int(level_counts.iloc[1])
                    middle_pct = (middle_count / total_levels) * 100
                    st.markdown(f"- Selanjutnya, terdapat **{middle_count}** individu ({middle_pct:.2f}%) yang berada pada tingkat **{middle_level}**.")
                
                # Mengambil data minoritas (paling sedikit)
                if len(level_counts) > 1:
                    lowest_level = level_counts.index[-1]
                    lowest_count = int(level_counts.iloc[-1])
                    lowest_pct = (lowest_count / total_levels) * 100
                    st.markdown(f"- Kelompok paling sedikit berada pada kategori **{lowest_level}** sebanyak **{lowest_count}** orang ({lowest_pct:.2f}%).")

                # Logika Peringatan / Sukses berdasarkan kategori yang mendominasi
                if dominant_level == "Healthy":
                    if dominant_pct > 70:
                        st.success(f"- **Sangat Baik!** Sebagian besar kelompok ini ({dominant_pct:.2f}%) memiliki kondisi kesehatan finansial yang prima.")
                elif dominant_level in ["Unhealthy", "At Risk"]:
                    st.error(f"- **Perhatian:** Tingkat kesehatan finansial didominasi oleh kategori **{dominant_level}**. Kelompok ini mungkin membutuhkan strategi perencanaan keuangan yang lebih ketat.")

        else:
            st.warning("Tidak ada data tingkat kesehatan finansial.")
            
    with col_d:
        status_counts = df['FinancialStatus'].value_counts()
        if not status_counts.empty:
            max_val5 = status_counts.max()
            colors5 = ['#3a86c8' if count == max_val5 else '#708090' for count in status_counts]
            
            fig5, ax5 = plt.subplots(figsize=(5, 3.5))
            
            ax5.set_position([0.1, 0.15, 0.8, 0.75])
            
            wedges, texts, autotexts = ax5.pie(
                status_counts, 
                autopct='%1.2f%%', 
                colors=colors5, 
                wedgeprops={'width': 0.7}
            )
            
            ax5.set_title("Distribution of Financial Status", pad=5)
            
            ax5.legend(
                wedges, 
                status_counts.index, 
                loc="upper center", 
                bbox_to_anchor=(0.5, -0.02), 
                ncol=2, 
                frameon=False
            )
            
            st.pyplot(fig5, bbox_inches=None)
            
            # Insight
            total_status = int(status_counts.sum())
            
            if total_status > 0:
                # Mengambil data posisi pertama (kategori dominan)
                dominant_status = status_counts.idxmax()
                dominant_count = int(status_counts.max())
                dominant_pct = (dominant_count / total_status) * 100
                
                st.markdown("##### 💡 Insight Status:")
                st.markdown(f"- Status finansial kelompok ini didominasi oleh kondisi **{dominant_status}** dengan total **{dominant_count}** individu ({dominant_pct:.2f}%).")
                
                # Mengambil data minoritas jika ada lebih dari 1 kategori
                if len(status_counts) > 1:
                    lowest_status = status_counts.idxmin()
                    lowest_count = int(status_counts.min())
                    lowest_pct = (lowest_count / total_status) * 100
                    st.markdown(f"- Sementara itu, terdapat **{lowest_count}** individu ({lowest_pct:.2f}%) yang berada dalam kondisi **{lowest_status}**.")

                # Logika Peringatan / Sukses berdasarkan status dominan
                if dominant_status == "Surplus":
                    st.success(f"- **Kondisi Positif:** Sebagian besar individu dalam kelompok ini berhasil menjaga pengeluarannya tetap di bawah pendapatan (Surplus).")
                elif dominant_status == "Deficit":
                    st.error(f"- **Peringatan Kritis:** Mayoritas kelompok mengalami **Deficit**, yang berarti pengeluaran bulanan mereka sudah melampaui total pemasukan.")

        else:
            st.warning("Tidak ada data status finansial.")
    
with tab4:
    st.header("Analisis A/B Testing (Statistik Inferensial)")
    st.markdown("Eksperimen statistik untuk membuktikan hubungan antar variabel finansial berdasarkan pengujian.")
    
    if df.empty:
        st.warning("Data tidak tersedia untuk dilakukan uji statistik. Harap sesuaikan filter Anda.")
    else:
        # --- SKENARIO 1 ---
        with st.expander("Skenario 1: Entertainment Expense (Surplus vs Deficit) - T-Test", expanded=True):
            st.markdown("**H0:** Tidak ada perbedaan rata-rata Entertainment Expense antara kelompok Surplus dan Deficit.")
            st.markdown("**H1:** Terdapat perbedaan rata-rata Entertainment Expense yang signifikan antara kelompok Surplus dan Deficit.")
            
            # Filter Data
            df_ab1 = df[df['FinancialStatus'].isin(['Surplus', 'Deficit'])]
            group_surplus = df_ab1[df_ab1['FinancialStatus'] == 'Surplus']['EntertainmentExpense']
            group_deficit = df_ab1[df_ab1['FinancialStatus'] == 'Deficit']['EntertainmentExpense']
            
            if not group_surplus.empty and not group_deficit.empty:
                # Kalkulasi Statistik
                t_stat1, p_value1 = stats.ttest_ind(group_surplus, group_deficit, equal_var=False, nan_policy='omit')
                
                # Visualisasi
                fig_ab1, ax_ab1 = plt.subplots(figsize=(5, 4))
                sns.barplot(
                    x='FinancialStatus', y='EntertainmentExpense', data=df_ab1,
                    palette={'Surplus': '#3a86c8', 'Deficit': '#e63946'},
                    capsize=0.1, errorbar='ci', ax=ax_ab1
                )
                
                ax_ab1.set_title("Average Entertainment Expense\nSurplus vs Deficit", pad=15, fontweight='bold')
                ax_ab1.set_xlabel("Financial Status", fontweight='bold')
                ax_ab1.set_ylabel("Entertainment Expense", fontweight='bold')
                
                # Ambil batas atas tertinggi dari grafik saat ini
                current_max_y = ax_ab1.get_ylim()[1]
                
                ax_ab1.set_ylim(0, current_max_y * 1.4)
                
                sig_text1 = f"T-Stat: {t_stat1:.2f} | P-Value: {p_value1:.4f}\n({'Significant' if p_value1 < 0.05 else 'Not Significant'})"
                
                ax_ab1.text(
                    0.5, 0.95, sig_text1,
                    transform=ax_ab1.transAxes,
                    ha='center', va='top', fontsize=9, color='black',
                    bbox=dict(facecolor='#f8f9fa', edgecolor='gray', boxstyle='round,pad=0.4')
                )
                
                plt.tight_layout()
                st.pyplot(fig_ab1, use_container_width=False)
                
                # Insight
                if p_value1 < 0.05:
                    st.success(f"**Kesimpulan (Tolak H0):** Terdapat perbedaan yang **SIGNIFIKAN** secara statistik pada Entertainment Expense.\n\n"
                        f"Rata-rata Entertainment Expense kelompok Deficit (**{group_deficit.mean():.2f}**) terbukti lebih tinggi "
                        f"dibandingkan kelompok Surplus (**{group_surplus.mean():.2f}**).")
                else:
                    st.info("**Kesimpulan (Gagal Tolak H0):** Tidak ada perbedaan yang signifikan pada Entertainment Expense antara individu Surplus dan Deficit.")
            else:
                st.warning("Data Surplus atau Deficit tidak cukup untuk diuji.")
                
        
        # --- SKENARIO 2 ---
        with st.expander("Skenario 2: Category Leaks based on Savings Status - Chi-Square"):
            st.markdown("**H0:** Tidak ada hubungan yang signifikan antara Savings Status dan Category Leaks (jumlah kategori Over Budget).")
            st.markdown("**H1:** Terdapat hubungan yang signifikan antara Savings Status dan Category Leaks (jumlah kategori Over Budget).")
            
            def kelompokkan_kebocoran(x):
                if x == 0: return '0 Leaks'
                elif x <= 2: return '1-2 Leaks'
                else: return '>2 Leaks'

            df['KebocoranCategory'] = df['OverBudgetCount'].apply(kelompokkan_kebocoran)
            df_filtered = df[df['SavingsStatus'].isin(['Healthy Saving', 'Low Saving'])]
            
            if not df_filtered.empty:
                contingency_table = pd.crosstab(df_filtered['SavingsStatus'], df_filtered['KebocoranCategory'])
                chi2_stat, p_value3, dof, expected = chi2_contingency(contingency_table)
                
                # Visualisasi
                fig_ab3, ax_ab3 = plt.subplots(figsize=(5, 3.2))
                sns.countplot(
                    data=df_filtered, x='SavingsStatus', hue='KebocoranCategory',
                    hue_order=['0 Leaks', '1-2 Leaks', '>2 Leaks'],
                    palette=['#2a9d8f', '#e9c46a', '#e76f51'], ax=ax_ab3
                )
                
                # Menambahkan label angka pasti di atas setiap batang
                for container in ax_ab3.containers:
                    ax_ab3.bar_label(container, padding=2, fontweight='bold', color='#333333', fontsize=8)

                ax_ab3.set_title("Category Leaks based on Savings Status", pad=15, fontweight='bold', fontsize=10)
                ax_ab3.set_xlabel("Savings Status", fontweight='bold', fontsize=9)
                ax_ab3.set_ylabel("Number of Individuals", fontweight='bold', fontsize=9)
                ax_ab3.legend(title="Leak Level", title_fontsize='8', fontsize='7')
                
                current_max_y3 = ax_ab3.get_ylim()[1]
                ax_ab3.set_ylim(0, current_max_y3 * 1.4)
                
                # Anotasi Statistik
                sig_text3 = f"Chi-Square: {chi2_stat:.2f} | P-Value: {p_value3:.4f}\n({'Significant' if p_value3 < 0.05 else 'Not Significant'})"
                
                ax_ab3.text(
                    0.5, 0.95, sig_text3, transform=ax_ab3.transAxes,
                    ha='center', va='top', fontsize=8, color='black',
                    bbox=dict(facecolor='#f8f9fa', edgecolor='gray', boxstyle='round,pad=0.3')
                )
                
                plt.tight_layout()
                st.pyplot(fig_ab3, use_container_width=False) 
                
                # Insight
                if p_value3 < 0.05:
                    st.success(
                        "**Kesimpulan (Tolak H0):** Terdapat hubungan yang **SIGNIFIKAN** secara statistik.\n\n"
                        "Ditemukan kelompok menarik di mana kelompok **Low Saving** didominasi oleh individu yang sangat disiplin (**0 Leaks**), "
                        "sedangkan kelompok **Healthy Saving** justru memiliki toleransi jumlah **>2 Leaks** yang cukup tinggi."
                    )
                else:
                    st.info("**Kesimpulan (Gagal Tolak H0):** Tidak ada hubungan yang signifikan antara Savings Status dan Category Leaks.")
            else:
                st.warning("Data Healthy Saving atau Low Saving tidak cukup untuk diuji.")