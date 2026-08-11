import streamlit as st

# 1. 기본 페이지 설정 (타이틀, 레이아웃 등)
st.set_page_config(
    page_title="도로설계 수리계산 프로그램",
    page_icon="🛣️",
    layout="wide"
)

# 2. 각 페이지 정의 (파일 경로, 메뉴에 표시될 이름, 아이콘)
home_page = st.Page("pages/home.py", title="메인화면", icon="🏠", default=True)
hydro_page = st.Page("pages/hydro_calc.py", title="수리계산서", icon="🌊")

# 3. 카테고리(그룹)별 메뉴 구성
pg = st.navigation({
    "메인": [home_page],
    "배수공": [hydro_page]  # 나중에 암거계산서, 집수정계산서 등을 여기에 추가하시면 됩니다.
})

# 4. 내비게이션 실행
pg.run()
