import streamlit as st

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="도로설계 통합 프로그램",
    page_icon="🛣️",
    layout="wide"
)

# 2. 공종별 하위 폴더 경로 지정 (경로는 영문, 화면 표시는 한글)
home_page = st.Page("pages/00_main/home.py", title="메인화면", icon="🏠", default=True)
earthwork_page = st.Page("pages/01_earthwork/earthwork.py", title="토공 계산", icon="🚜")
u_channel_page = st.Page("pages/02_drainage/u_channel.py", title="U형측구 수리계산서", icon="🌊")
pavement_page = st.Page("pages/03_pavement/pavement.py", title="포장공 계산", icon="🛣️")
subsidiary_page = st.Page("pages/04_subsidiary/subsidiary.py", title="부대공 계산", icon="🏗️")
etc_page = st.Page("pages/05_etc/etc.py", title="기타 계산/도구", icon="📂")

# 3. 사이드바 카테고리(그룹) 구성 (그룹명도 한글)
pg = st.navigation({
    "메인": [home_page],
    "토공": [earthwork_page],
    "배수공": [u_channel_page],
    "포장공": [pavement_page],
    "부대공": [subsidiary_page],
    "기타": [etc_page]
})

# 4. 내비게이션 실행
pg.run()