# dashboard.py
"""
===============================================================================
DASHBOARD ANALISIS BIKE SHARING (2011-2012)
===============================================================================
===============================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from pathlib import Path
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')

DATA_DIR = Path(__file__).parent

# ==============================================================================
# KONFIGURASI VISUAL
# ==============================================================================
class VisualConfig:
    COLORS = {
        "registered": "#2E86AB",
        "casual": "#E67E22",
        "clear": "#27AE60",
        "rain": "#C0392B",
        "primary": "#1E3A5F",
        "secondary": "#6C757D",
        "grid": "#DEE2E6",
        "text_primary": "#212529",
        "text_secondary": "#6C757D",
    }
    
    FONTS = {
        "title_large": 24,
        "title": 18,
        "body": 14,
        "caption": 12,
        "annotation": 10,
    }
    
    CHART = {
        "figure_dpi": 120,
        "grid_alpha": 0.25,
        "bar_width": 0.35,
        "line_width": 2.5,
        "marker_size": 7,
    }

CONFIG = VisualConfig()

# Set Matplotlib Style
plt.rcParams.update({
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'font.family': 'sans-serif',
    'font.size': CONFIG.FONTS['body'],
    'axes.spines.top': False,
    'axes.spines.right': False,
    'figure.dpi': CONFIG.CHART['figure_dpi'],
})


# ==============================================================================
# DATA LOADING
# ==============================================================================
@st.cache_data(ttl=3600)
def load_all_data():
    """Memuat semua file CSV dari folder data/dashboard/"""
    
    # Cek apakah folder data ada
    if not DATA_DIR.exists():
        st.error(f"❌ Folder data tidak ditemukan di: {DATA_DIR}")
        st.info("Pastikan folder 'data/dashboard/' berada di lokasi yang sama dengan dashboard.py")
        st.stop()
    
    required_files = {
        "hourly": "hourly_pattern.csv",
        "weather": "weather_impact.csv",
        "main": "main_data.csv"
    }
    
    dataframes = {}
    
    for key, filename in required_files.items():
        file_path = DATA_DIR / filename
        try:
            if file_path.exists():
                df = pd.read_csv(file_path)
                
                # Post-processing main_data
                if key == "main" and 'date' in df.columns:
                    df['date'] = pd.to_datetime(df['date'])
                    df['year'] = df['date'].dt.year
                
                dataframes[key] = df
                st.sidebar.success(f"✅ {filename}")
            else:
                st.error(f"❌ File tidak ditemukan: {file_path}")
                st.stop()
        except Exception as e:
            st.error(f"⚠️ Gagal membaca {filename}: {e}")
            st.stop()
    
    return dataframes


# ==============================================================================
# VISUALIZATION FUNCTIONS
# ==============================================================================
def apply_tufte_style(ax, title=None, xlabel=None, ylabel=None):
    """Menerapkan prinsip Data-Ink Ratio Tufte."""
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(CONFIG.COLORS['grid'])
    ax.spines['bottom'].set_color(CONFIG.COLORS['grid'])
    
    ax.yaxis.grid(True, linestyle='-', alpha=CONFIG.CHART['grid_alpha'], 
                  color=CONFIG.COLORS['grid'])
    ax.xaxis.grid(False)
    ax.set_axisbelow(True)
    
    y_min, y_max = ax.get_ylim()
    ax.set_ylim(0, y_max * 1.08)
    
    if title:
        ax.set_title(title, fontsize=CONFIG.FONTS['title'], 
                    fontweight='600', pad=20, loc='left')
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=CONFIG.FONTS['body'])
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=CONFIG.FONTS['body'])
    
    ax.tick_params(colors=CONFIG.COLORS['text_secondary'], 
                   labelsize=CONFIG.FONTS['caption'])
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'{int(x):,}'))
    
    return ax


def plot_hourly_pattern(df_hourly):
    """Plot pola sewa per jam."""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    hours = df_hourly['hr'].values
    registered = df_hourly['registered'].values
    casual = df_hourly['casual'].values
    
    # Area fill
    ax.fill_between(hours, registered, alpha=0.08, color=CONFIG.COLORS['registered'])
    ax.fill_between(hours, casual, alpha=0.08, color=CONFIG.COLORS['casual'])
    
    # Plot garis
    ax.plot(hours, registered, color=CONFIG.COLORS['registered'], 
            linewidth=CONFIG.CHART['line_width'], marker='o', 
            markersize=CONFIG.CHART['marker_size'], markerfacecolor='white',
            markeredgewidth=2, markeredgecolor=CONFIG.COLORS['registered'],
            label='Registered')
    
    ax.plot(hours, casual, color=CONFIG.COLORS['casual'], 
            linewidth=CONFIG.CHART['line_width'], marker='s', 
            markersize=CONFIG.CHART['marker_size'], markerfacecolor='white',
            markeredgewidth=2, markeredgecolor=CONFIG.COLORS['casual'],
            label='Casual')
    
    # Temukan puncak
    max_reg_idx = np.argmax(registered)
    max_cas_idx = np.argmax(casual)
    
    # Anotasi
    ax.annotate(f"{registered[max_reg_idx]:,}",
               xy=(hours[max_reg_idx], registered[max_reg_idx]),
               xytext=(hours[max_reg_idx], registered[max_reg_idx] + max(registered)*0.1),
               fontsize=CONFIG.FONTS['annotation'], fontweight='bold',
               color=CONFIG.COLORS['registered'], ha='center',
               bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=CONFIG.COLORS['registered'], alpha=0.8))
    
    ax.annotate(f"{casual[max_cas_idx]:,}",
               xy=(hours[max_cas_idx], casual[max_cas_idx]),
               xytext=(hours[max_cas_idx], casual[max_cas_idx] - max(casual)*0.12),
               fontsize=CONFIG.FONTS['annotation'], fontweight='bold',
               color=CONFIG.COLORS['casual'], ha='center',
               bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=CONFIG.COLORS['casual'], alpha=0.8))
    
    ax = apply_tufte_style(ax,
                          title="📈 Pola Sewa Sepeda per Jam: Registered vs Casual",
                          xlabel="Jam dalam Sehari",
                          ylabel="Rata-rata Jumlah Sewa")
    
    ax.set_xticks(range(0, 24, 2))
    ax.set_xticklabels([f"{h:02d}:00" for h in range(0, 24, 2)])
    ax.set_xlim(-0.5, 23.5)
    
    ax.legend(loc='upper right', frameon=True, edgecolor='none', facecolor='white', framealpha=0.9)
    
    plt.tight_layout()
    
    return fig, hours[max_reg_idx], registered[max_reg_idx], hours[max_cas_idx], casual[max_cas_idx]


def plot_weather_impact(df_weather):
    """Plot dampak cuaca."""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    categories = ['Total', 'Registered', 'Casual']
    
    total_row = df_weather[df_weather['metric'] == 'total'].iloc[0]
    reg_row = df_weather[df_weather['metric'] == 'registered'].iloc[0]
    cas_row = df_weather[df_weather['metric'] == 'casual'].iloc[0]
    
    clear_vals = [total_row['clear_avg'], reg_row['clear_avg'], cas_row['clear_avg']]
    rain_vals = [total_row['precip_avg'], reg_row['precip_avg'], cas_row['precip_avg']]
    pct_changes = [total_row['pct_change'], reg_row['pct_change'], cas_row['pct_change']]
    
    x = np.arange(len(categories))
    width = CONFIG.CHART['bar_width']
    
    ax.bar(x - width/2, clear_vals, width, label='Cerah', 
           color=CONFIG.COLORS['clear'], edgecolor='white', linewidth=1)
    ax.bar(x + width/2, rain_vals, width, label='Hujan/Salju', 
           color=CONFIG.COLORS['rain'], edgecolor='white', linewidth=1)
    
    # Anotasi persentase
    for i, pct in enumerate(pct_changes):
        y_pos = min(clear_vals[i], rain_vals[i]) * 0.5
        color = '#C0392B' if pct < -40 else '#E67E22' if pct < -30 else '#F39C12'
        ax.text(i, y_pos, f'{pct:.1f}%', ha='center', va='center',
               fontsize=13, fontweight='bold', color='black',
               bbox=dict(boxstyle='round,pad=0.4', facecolor=color, edgecolor='none', alpha=0.85))
    
    ax = apply_tufte_style(ax,
                          title="🌧️ Dampak Cuaca Buruk terhadap Volume Sewa",
                          ylabel="Rata-rata Jumlah Sewa Harian")
    
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.legend(loc='upper right', frameon=True, edgecolor='none', facecolor='white', framealpha=0.9)
    
    plt.tight_layout()
    
    return fig, pct_changes


# ==============================================================================
# CUSTOM CSS
# ==============================================================================
def inject_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }
        
        .main-header {
            padding: 20px 0;
            border-bottom: 2px solid #E9ECEF;
            margin-bottom: 24px;
        }
        
        .main-title {
            font-size: 32px;
            font-weight: 700;
            color: #f5b342;
        }
        
        .metric-card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            border: 1px solid #E9ECEF;
            text-align: center;
        }
        
        .metric-value {
            font-size: 32px;
            font-weight: 700;
            color: #1E3A5F;
        }
        
        .metric-label {
            font-size: 12px;
            text-transform: uppercase;
            color: #6C757D;
            letter-spacing: 0.5px;
        }
        
        .insight-box {
            background: linear-gradient(135deg, #1a4066 0%, #1a4066 100%);
            border-left: 4px solid #F39C12;
            border-radius: 8px;
            padding: 18px 24px;
            margin: 20px 0;
            color: white;
        }
        
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)


# ==============================================================================
# MAIN APP
# ==============================================================================
def main():
    st.set_page_config(
        page_title="Bike Sharing Dashboard",
        page_icon="🚲",
        layout="wide"
    )
    
    inject_css()
    
    # Load data
    data = load_all_data()
    df_hourly = data['hourly']
    df_weather = data['weather']
    df_main = data['main']
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🚲 Bike Sharing")
        st.markdown("### 📅 Filter")
        
        year_options = ["Semua Data", 2011, 2012]
        year_filter = st.selectbox("Pilih Tahun:", year_options)
        
        st.markdown("---")
        st.markdown("### 📊 Info Dataset")
        st.metric("Total Hari", f"{len(df_main):,}")

        
        # Export button
        if year_filter != "Semua Data":
            export_df = df_main[df_main['year'] == int(year_filter)]
        else:
            export_df = df_main
            
        csv = export_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f'bike_sharing_{year_filter}.csv',
            mime='text/csv'
        )
    
    # Main Content
    st.markdown("""
    <div class="main-header">
        <div class="main-title">🚲 Dashboard Analisis Bike Sharing</div>
        <p style="color: #6C757D; font-size: 16px;">Washington D.C. • 2011-2012</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ======================================================================
    # SECTION 1: HOURLY PATTERN
    # ======================================================================
    st.markdown("## 📈 1. Analisis Pola Sewa per Jam")
    
    fig1, reg_hour, reg_val, cas_hour, cas_val = plot_hourly_pattern(df_hourly)
    
    # KPI Cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">⏰ Puncak Registered</div>
            <div class="metric-value">{int(reg_hour):02d}:00</div>
            <div style="color: #6C757D;">{int(reg_val):,} sewa</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🌙 Puncak Casual</div>
            <div class="metric-value">{int(cas_hour):02d}:00</div>
            <div style="color: #6C757D;">{int(cas_val):,} sewa</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        delta = int(reg_val - cas_val)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📊 Selisih Volume</div>
            <div class="metric-value">{delta:,}</div>
            <div style="color: #6C757D;">Registered > Casual</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.pyplot(fig1)
    
    st.markdown("""
    <div class="insight-box">
        <h4 style="margin: 0 0 10px 0; color: #F39C12;">💡 Insight Bisnis</h4>
        <p style="margin: 0; line-height: 1.6;">
            <strong>Registered</strong> memuncak pada jam sibuk pagi (08:00) dan sore (17:00-18:00), 
            menunjukkan penggunaan untuk komuter. <strong>Casual</strong> memuncak pada siang hari (13:00-15:00), 
            mengindikasikan penggunaan rekreasi. Strategi penempatan sepeda sebaiknya disesuaikan dengan pola ini.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ======================================================================
    # SECTION 2: WEATHER IMPACT
    # ======================================================================
    st.markdown("## 🌧️ 2. Analisis Dampak Cuaca")
    
    fig2, pct_changes = plot_weather_impact(df_weather)
    
    # KPI Cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📉 Penurunan Total</div>
            <div class="metric-value" style="color: #C0392B;">{pct_changes[0]:.1f}%</div>
            <div style="color: #6C757D;">saat hujan/salju</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📉 Penurunan Registered</div>
            <div class="metric-value" style="color: #E67E22;">{pct_changes[1]:.1f}%</div>
            <div style="color: #6C757D;">lebih tahan cuaca</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📉 Penurunan Casual</div>
            <div class="metric-value" style="color: #C0392B;">{pct_changes[2]:.1f}%</div>
            <div style="color: #6C757D;">sensitif cuaca</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.pyplot(fig2)
    
    st.markdown(f"""
    <div class="insight-box">
        <h4 style="margin: 0 0 10px 0; color: #F39C12;">💡 Insight Bisnis</h4>
        <p style="margin: 0; line-height: 1.6;">
            Hujan/salju ringan menyebabkan penurunan total sewa hingga <strong>{abs(pct_changes[0]):.1f}%</strong>.
            Penurunan terbesar terjadi pada segmen <strong>Casual ({pct_changes[2]:.1f}%)</strong> dibandingkan
            <strong>Registered ({pct_changes[1]:.1f}%)</strong>. Pengguna berlangganan lebih inelastis terhadap cuaca.
            Promosi khusus saat cuaca buruk dapat menargetkan segmen casual.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="display: flex; justify-content: space-between; color: #6C757D; font-size: 13px; padding: 20px 0;">
        <span>© 2024 Bike Sharing Analytics Dashboard</span>
        <span>Data: 2011-2012 • Dibangun dengan Streamlit</span>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
