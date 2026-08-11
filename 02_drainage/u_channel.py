import os
import streamlit as st
import pandas as pd
import numpy as np

# ⚠️ 주의: st.set_page_config(...)는 main.py에서 이미 선언했으므로 
# 하위 페이지인 이 파일에서는 삭제하거나 주석 처리해야 에러가 발생하지 않습니다.

@st.cache_data
def load_rainfall_data():
    # 1. 현재 파일(u_channel.py)이 위치한 폴더('02_drainage') 경로 자동 탐색
    current_dir = os.path.dirname(__file__)
    
    # 2. 해당 폴더 안에 있는 'idf.xls' 파일의 정확한 절대 경로 생성
    excel_path = os.path.join(current_dir, 'idf.xls')
    
    # 3. 완성된 경로로 엑셀 읽기
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
    # ... (이 아래부터는 기존 코드와 완전히 동일하게 유지하시면 됩니다.) ...

def calculate_u_type_ditch():
    try:
        regions_dict = load_rainfall_data()
        region_list = sorted(list(regions_dict.keys()))
    except Exception as e:
        st.error(f"엑셀 파일 읽기 오류: {e}")
        return
    
    st.sidebar.header("📝 일반사항")
    
    default_region_idx = region_list.index("강릉") if "강릉" in region_list else 0
    selected_region = st.sidebar.selectbox("지역 선택", region_list, index=default_region_idx)
    
    available_T = sorted(list(regions_dict[selected_region].keys()))
    default_T_idx = available_T.index(10) if 10 in available_T else 0
    selected_T = st.sidebar.selectbox("재현기간 (년)", available_T, index=default_T_idx)
    
    default_I = float(regions_dict[selected_region][selected_T])
    I_rain = st.sidebar.number_input("강우강도 (I, mm/hr)", value=default_I, format="%.3f", step=0.1)
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("💧 유출계수(C) 설정")
    
    runoff_coeffs = {
        "포장면 : 0.9": 0.9,
        "가파른 산지 및 비탈면 : 0.8": 0.8,
        "가파른 계곡 경작지 : 0.8": 0.8,
        "논 : 0.8": 0.8,
        "완만한 산지 : 0.7": 0.7,
        "완만한 경작지 : 0.7": 0.7,
        "도시지역 : 0.7": 0.7,
        "잡지 : 0.6": 0.6,
        "경작하는 평계곡 : 0.6": 0.6,
        "경작하는 평작지 : 0.5": 0.5,
        "수림 : 0.3": 0.3,
        "밀림수림과 덤불숲 : 0.2": 0.2
    }
    
    with st.sidebar.expander("유출계수 선택 표 열기"):
        selected_option = st.selectbox("지표면 상태 선택", list(runoff_coeffs.keys()), index=6)
        
    C = runoff_coeffs[selected_option]
    label_name = selected_option.split(" : ")[0]
    
    A_catch = st.sidebar.number_input("유역면적 (A, ㎢)", value=0.0011, format="%.4f", step=0.0001)
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("측구 제원")
    
    B = st.sidebar.number_input("폭 (B, m)", value=0.68, step=0.01, format="%.3f")
    H = st.sidebar.number_input("높이 (H, m)", value=0.25, step=0.01, format="%.3f")
    n = st.sidebar.number_input("조도계수 (n)", value=0.015, format="%.3f")
    slope_pct = st.sidebar.number_input("수로경사 (%)", value=0.1, step=0.01, format="%.3f")

    st.title("🌊 U형측구 수리계산서")
    
    Qd = 0.278 * C * I_rain * A_catch
    
    st.header("[1] 설계유량(Qd) 계산")
    st.write(f" - 선택 지역 : **{selected_region}**")
    st.write(f" - 재현기간 : **{int(selected_T)}년**")
    st.write(f" - 공식 : Qd = 0.278 × C × I × A")
    st.write(f" - 유출계수(C) : {C:.3f} ({label_name})")
    st.write(f" - 강우강도(I) : {I_rain:.3f} mm/hr")
    st.write(f" - 유역면적(A) : {A_catch:.3f} ㎢")
    st.info(f"▶ 설계유량(Qd) = 0.278 × {C:.3f} × {I_rain:.3f} × {A_catch:.3f} = **{Qd:.3f} ㎥/sec**")
    
    effective_H = 0.8 * H
    A_c = B * effective_H
    P = B + 2 * effective_H
    R = A_c / P
    
    st.header("[2] 측구 단면 특성 (안전율 80% 적용)")
    
    svg_code = f"""
    <div style="display: flex; justify-content: flex-start; margin: 10px 0;">
        <svg width="450" height="230" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="black" />
            </marker>
            <marker id="arrow-blue" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#0066cc" />
            </marker>
          </defs>
          <rect x="100" y="40" width="240" height="160" fill="#e0e0e0" />
          <rect x="120" y="40" width="200" height="140" fill="white" />
          <rect x="120" y="{180 - (effective_H / H) * 140}" width="200" height="{(effective_H / H) * 140}" fill="#a0c8f0" opacity="0.8" />
          <path d="M 120 40 L 120 180 L 320 180 L 320 40" fill="none" stroke="#555" stroke-width="4"/>
          <line x1="120" y1="20" x2="320" y2="20" stroke="black" stroke-width="1.5" marker-start="url(#arrow)" marker-end="url(#arrow)"/>
          <text x="220" y="12" font-family="sans-serif" font-size="13" font-weight="bold" text-anchor="middle">폭(B) = {B:.3f} m</text>
          <line x1="80" y1="40" x2="80" y2="180" stroke="black" stroke-width="1.5" marker-start="url(#arrow)" marker-end="url(#arrow)"/>
          <text x="70" y="110" font-family="sans-serif" font-size="13" font-weight="bold" text-anchor="middle" transform="rotate(-90 70,110)">높이(H) = {H:.3f} m</text>
          <line x1="340" y1="{180 - (effective_H / H) * 140}" x2="340" y2="180" stroke="#0066cc" stroke-width="1.5" marker-start="url(#arrow-blue)" marker-end="url(#arrow-blue)"/>
          <text x="365" y="110" font-family="sans-serif" font-size="13" font-weight="bold" fill="#0066cc" text-anchor="middle" transform="rotate(90 365,110)">유효수심 = {effective_H:.3f} m</text>
        </svg>
    </div>
    """
    st.markdown(svg_code, unsafe_allow_html=True)

    st.write(f" - 측구 제원 : 폭(B) = {B:.3f} m, 높이(H) = {H:.3f} m")
    st.write(f" - 유효 수심 (0.8H) = {effective_H:.3f} m")
    st.write(f" - 통수단면적(A) = B × 0.8H = {B:.3f} × {effective_H:.3f} = {A_c:.3f} ㎡")
    st.write(f" - 윤변(P) = B + (0.8H × 2) = {B:.3f} + {effective_H*2:.3f} = {P:.3f} m")
    st.write(f" - 동수반경(R) = A / P = {A_c:.3f} / {P:.3f} = {R:.3f} m")

    I_slope = slope_pct / 100
    V = (1/n) * (R ** (2/3)) * (I_slope ** 0.5)
    Q = A_c * V
    
    st.header("[3] 평균 유속(V) 및 통수유량(Q) 계산 (Manning 공식)")
    st.write(f" - 조도계수(n) : {n:.3f} (콘크리트)")
    st.write(f" - 수로경사(I) : {slope_pct:.3f}% = {I_slope:.3f}")
    st.write(f" - 평균유속(V) = (1/n) × R^(2/3) × I^(1/2)")
    st.write(f" &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;= (1/{n:.3f}) × {R:.3f}^(2/3) × {I_slope:.3f}^(1/2) = {V:.3f} m/sec")
    st.info(f"▶ 통수유량(Q) = A × V = {A_c:.3f} × {V:.3f} = **{Q:.3f} ㎥/sec**")
    
    is_safe = Qd < Q
    status = "OK (안전)" if is_safe else "NG (위험)"
    
    st.header("[4] 수리검토 결과 요약")
    st.write(f" - 발생 설계유량 (Qd) : {Qd:.3f} ㎥/sec")
    st.write(f" - 측구 통수유량 (Q)  : {Q:.3f} ㎥/sec")
    
    if is_safe:
        st.success(f"▶ 판정 : Qd({Qd:.3f}) < Q({Q:.3f}) ➔ **{status}**")
    else:
        st.error(f"▶ 판정 : Qd({Qd:.3f}) >= Q({Q:.3f}) ➔ **{status}**")

    # PDF 저장 버튼 (인쇄 창 호출)
    st.markdown("---")
    st.subheader("📄 수리계산서 출력")
    st.markdown(
    """
    <div style="margin: 10px 0;">
        <button onclick="window.parent.print()" style="padding: 10px 20px; font-size: 16px; background-color: #0066cc; color: white; border: none; border-radius: 5px; cursor: pointer;">
            🖨️ PDF로 저장하기 (인쇄)
        </button>
    </div>
    """,
    unsafe_allow_html=True
    )

if __name__ == "__main__":
    calculate_u_type_ditch()