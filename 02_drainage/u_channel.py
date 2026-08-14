import os
import streamlit as st
import pandas as pd
import numpy as np

# ⚠️ [중요] st.set_page_config()는 main.py에서 이미 실행되었으므로 
# 이 파일에서는 절대로 작성하면 안 됩니다. (오류 발생의 주원인)

@st.cache_data
def load_rainfall_data():
    # 현재 u_channel.py 파일이 있는 폴더(02_drainage) 경로 자동 인식
    current_dir = os.path.dirname(__file__)
    excel_path = os.path.join(current_dir, 'idf.xls')
    
    xls = pd.ExcelFile(excel_path)
    regions_dict = {}
    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name)
        data = df.iloc[5:18, [1, 2]].copy()
        data.columns = ['T', 'intensity']
        data['T'] = pd.to_numeric(data['T'], errors='coerce')
        data['intensity'] = pd.to_numeric(data['intensity'], errors='coerce')
        data = data.dropna()
        regions_dict[sheet_name] = data.set_index('T')['intensity'].to_dict()
    return regions_dict

def calculate_u_type_ditch():
    st.title("🌊 U형측구 수리계산서")
    
    try:
        regions_dict = load_rainfall_data()
        region_list = sorted(list(regions_dict.keys()))
    except Exception as e:
        st.error(f"⚠️ 엑셀 파일(idf.xls) 읽기 오류: {e}")
        st.info("💡 'pages/02_drainage' 폴더 안에 'idf.xls' 파일이 존재하는지 확인해 주세요.")
        return
    
    st.sidebar.header("📝 일반사항 및 입력")
    
    default_region_idx = region_list.index("강릉") if "강릉" in region_list else 0
    selected_region = st.sidebar.selectbox("지역 선택", region_list, index=default_region_idx)
    freq = st.sidebar.selectbox("재현기간 (년)", [5, 10, 20, 30, 50, 100], index=1)
    tc = st.sidebar.number_input("지속시간 (분)", min_value=1.0, value=5.0, step=1.0)
    
    A = st.sidebar.number_input("유역면적 (ha)", min_value=0.0001, value=0.0500, format="%.4f")
    C = st.sidebar.number_input("유출계수 (C)", min_value=0.01, max_value=1.00, value=0.80, step=0.05)
    
    st.sidebar.header("📐 측구 제원")
    B = st.sidebar.number_input("측구 폭 B (m)", min_value=0.1, value=0.4, step=0.05)
    H = st.sidebar.number_input("측구 높이 H (m)", min_value=0.1, value=0.4, step=0.05)
    slope_pct = st.sidebar.number_input("수로경사 (%)", min_value=0.01, value=1.0, step=0.1)
    n = st.sidebar.number_input("조도계수 (n)", min_value=0.001, value=0.015, step=0.001, format="%.3f")
    
    # --- 강우강도 보간 계산 ---
    region_data = regions_dict[selected_region]
    times = np.array(sorted(region_data.keys()))
    intensities = np.array([region_data[t] for t in times])
    
    if tc in region_data:
        I = region_data[tc]
    else:
        I = float(np.interp(tc, times, intensities))
        
    # --- 1. 설계유량(Qd) 계산 ---
    Qd = (1 / 360) * C * I * A
    
    st.subheader("[1] 설계유량(Qd) 산출 (합리식)")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"- 선택 지역: **{selected_region}** ({freq}년 빈도)")
        st.write(f"- 강우지속시간(tc): **{tc:.1f} 분**")
        st.write(f"- 산출 강우강도(I): **{I:.2f} mm/hr**")
    with col2:
        st.write(f"- 유역면적(A): **{A:.4f} ha**")
        st.write(f"- 유출계수(C): **{C:.2f}**")
        st.info(f"▶ **설계유량 (Qd) = {Qd:.3f} ㎥/sec**")
        
    # --- 2. 통수유량(Q) 및 유속(V) 계산 ---
    A_c = B * H
    P = B + 2 * H
    R = A_c / P
    I_slope = slope_pct / 100
    V = (1 / n) * (R ** (2/3)) * (I_slope ** 0.5)
    Q = A_c * V
    
    st.subheader("[2] 단면제원 및 통수능력(Q) 계산 (Manning 공식)")
    col3, col4 = st.columns(2)
    with col3:
        st.write(f"- 단면적 (A): **{A_c:.3f} ㎡**")
        st.write(f"- 윤변 (P): **{P:.3f} m**")
        st.write(f"- 경심 (R = A/P): **{R:.3f} m**")
    with col4:
        st.write(f"- 평균유속 (V): **{V:.3f} m/sec**")
        st.info(f"▶ **통수유량 (Q) = {Q:.3f} ㎥/sec**")
        
    # --- 3. 안전성 판정 ---
    st.subheader("[3] 최종 안전성 판정")
    is_safe = Q >= Qd
    if is_safe:
        st.success(f"✅ **O.K.** (통수유량 Q = {Q:.3f} ㎥/s ≥ 설계유량 Qd = {Qd:.3f} ㎥/s)")
    else:
        st.error(f"❌ N.G. (통수유량 Q = {Q:.3f} ㎥/s < 설계유량 Qd = {Qd:.3f} ㎥/s — 단면 확장 필요)")

# 🚀 [핵심] 이 페이지가 열릴 때 메인 계산 함수를 실행합니다.
calculate_u_type_ditch()