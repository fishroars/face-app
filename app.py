import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import plotly.graph_objects as go
from PIL import Image
import math
import hashlib
import pandas as pd

# --- 1. 기본 설정 및 모바일 최적화 CSS ---
st.set_page_config(page_title="Biometric VIP Report", layout="centered", initial_sidebar_state="collapsed")

custom_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;700;900&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; color: #111; }
    .report-header { border-top: 4px solid #000; border-bottom: 2px solid #000; padding: 15px 0; margin-bottom: 15px; text-align: center;}
    .report-title { font-weight: 900; font-size: 20px; margin: 0; }
    .metric-row { display: flex; justify-content: space-between; border-bottom: 1px dashed #ccc; padding: 10px 0; font-size: 14px; }
    .highlight-box { background-color: #f8f9fa; border-left: 4px solid #000; padding: 15px; margin-top: 15px; font-size: 14px; line-height: 1.6; }
    .login-box { border: 1px solid #ddd; padding: 20px; border-radius: 10px; background-color: #fafafa; margin-top: 20px; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { font-weight: bold; padding: 10px 15px; }
    .guide-box { background-color: #e8f0fe; border-left: 4px solid #4285f4; padding: 10px; margin-bottom: 15px; font-size: 13px; color: #333; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ⭐️ [매우 중요] 아래 따옴표 안에 본인의 구글 시트 CSV 링크를 붙여넣으세요!
SHEET_URL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vS_PWLBFxD2ceR3l2SjyL1iNECdQ2i72TxyT39D7_YBCsvDIXK5zQteTqfRs1c6z451ZvbbzCMLrQnh/pub?output=csv'

# --- 2. 코어 수학 및 분석 로직 ---
@st.cache_data(ttl=60)
def load_allowed_users(url):
    try:
        return pd.read_csv(url)
    except:
        return None

def calc_3d_dist(p1, p2, w, h):
    dx, dy, dz = (p1.x - p2.x) * w, (p1.y - p2.y) * h, (p1.z - p2.z) * w 
    return math.sqrt(dx**2 + dy**2 + dz**2)

def analyze_face(image_array):
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=True)
    h, w, _ = image_array.shape
    results = face_mesh.process(image_array)
    
    if not results.multi_face_landmarks:
        return None, None, "❌ 얼굴을 인식하지 못했습니다. 머리카락이 눈이나 턱을 가리지 않게 해주세요."
        
    landmarks = results.multi_face_landmarks[0].landmark
    l_zygoma, r_zygoma = landmarks[234], landmarks[454]
    trichion, gnathion = landmarks[10], landmarks[152]
    nasion, stomion = landmarks[168], landmarks[13]
    l_pupil, r_pupil = landmarks[468], landmarks[473]
    pronasale = landmarks[1]

    # [수정됨] 허용 오차를 8도까지 대폭 완화! (사람이 편하게 찍을 수 있는 각도)
    dx = (r_pupil.x - l_pupil.x) * w
    dy = (r_pupil.y - l_pupil.y) * h
    tilt_angle = abs(math.degrees(math.atan2(dy, dx)))
    
    if tilt_angle > 8.0: 
        return None, None, f"⚠️ 고개가 너무 많이 꺾였습니다 ({tilt_angle:.1f}도). 갸우뚱하지 않게 정면을 봐주세요!"

    face_width = calc_3d_dist(l_zygoma, r_zygoma, w, h)
    face_height = calc_3d_dist(trichion, gnathion, w, h)
    upper_face_height = calc_3d_dist(nasion, stomion, w, h)
    
    fwhr = face_width / upper_face_height if upper_face_height > 0 else 0
    ip_index = (calc_3d_dist(l_pupil, r_pupil, w, h) / face_width) * 100 
    mf_index = (calc_3d_dist(nasion, stomion, w, h) / face_height) * 100 
    
    sym_diff = abs(calc_3d_dist(pronasale, l_zygoma, w, h) - calc_3d_dist(pronasale, r_zygoma, w, h)) / face_width * 100
    jaw_ratio = (calc_3d_dist(landmarks[132], landmarks[361], w, h) / face_width) * 100 
    
    sym_score = min(max(100 - (sym_diff * 12), 0), 100)
    baby_score = min(max(100 - (mf_index - 32) * 8, 0), 100) 
    dom_score = min(max((fwhr - 1.6) * 55 + 40, 0), 100) 
    trust_score = min(max((sym_score * 0.5) + (baby_score * 0.3) + 20, 0), 100) 
    ext_score = min(max((fwhr - 1.5) * 35 + trust_score * 0.2, 0), 100)
    comp_score = min(max(((100 - baby_score) * 0.4) + (sym_score * 0.4) + (dom_score * 0.2), 0), 100)
    
    bio_hash = hashlib.sha256(f"{pronasale.x}{l_zygoma.x}".encode('utf-8')).hexdigest()[:8].upper()
    
    metrics = {
        "hash": bio_hash, "fwhr": fwhr, "ip_index": ip_index, "mf_index": mf_index, "jaw_ratio": jaw_ratio,
        "scores": {"Trust": trust_score, "Competence": comp_score, "Dominance": dom_score, "Extravers": ext_score, "Neoteny": baby_score, "Symmetry": sym_score}
    }
    
    img_draw = image_array.copy()
    thickness = max(int(w / 400), 2)
    cv2.line(img_draw, (int(l_pupil.x*w), int(l_pupil.y*h)), (int(r_pupil.x*w), int(r_pupil.y*h)), (255,255,255), thickness)
    cv2.rectangle(img_draw, (int(l_zygoma.x*w), int(nasion.y*h)), (int(r_zygoma.x*w), int(stomion.y*h)), (255,255,255), thickness)

    return img_draw, metrics, None

# --- 3. 이메일 로그인 시스템 ---
if "access_granted" not in st.session_state:
    st.session_state["access_granted"] = False

if not st.session_state["access_granted"]:
    st.markdown('<div class="report-header"><p class="report-title">🔒 CLINICAL AI LOGIN</p></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    user_email = st.text_input("📧 이메일 (Email):", placeholder="example@email.com")
    user_pw = st.text_input("🔑 비밀번호 (Password):", type="password", placeholder="비밀번호 입력")
    
    if st.button("로그인", use_container_width=True):
        if '여기에_구글시트_CSV_링크를_붙여넣으세요' in SHEET_URL or 'docs.google.com' not in SHEET_URL:
            st.error("⚠️ 코드 31번째 줄의 SHEET_URL을 구글 시트 주소로 변경해주세요!")
        elif not user_email or not user_pw:
            st.warning("⚠️ 이메일과 비밀번호를 모두 입력해 주세요.")
        else:
            df_users = load_allowed_users(SHEET_URL)
            if df_users is not None:
                df_users['Email'] = df_users['Email'].astype(str).str.strip()
                df_users['Password'] = df_users['Password'].astype(str).str.strip()
                match = df_users[(df_users['Email'] == str(user_email).strip()) & (df_users['Password'] == str(user_pw).strip())]
                
                if not match.empty:
                    st.session_state["access_granted"] = True
                    st.session_state["user_name"] = match.iloc[0]['Name']
                    st.rerun()
                else:
                    st.error("❌ 이메일 또는 비밀번호가 일치하지 않습니다.")
            else:
                st.error("❌ 구글 시트를 불러올 수 없습니다.")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 4. 메인 대시보드 ---
col1, col2 = st.columns([7, 3])
with col1:
    st.markdown(f'<div style="font-weight:900; font-size:18px; margin-top:10px;">👤 {st.session_state["user_name"]} 님의 리포트</div>', unsafe_allow_html=True)
with col2:
    if st.button("로그아웃", use_container_width=True):
        st.session_state["access_granted"] = False
        st.rerun()

st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)

# [수정됨] 카메라 위에 사용자가 보기 편한 가이드라인 안내 박스 추가
st.markdown("""
<div class="guide-box">
    📸 <b>촬영 가이드 (AI 자동 보정 켜짐)</b><br>
    • 스마트폰 렌즈가 눈높이와 <b>일직선</b>이 되게 들어주세요.<br>
    • 카메라 화면의 <b>중앙에 얼굴이 가득 차도록</b> 맞춰주세요.<br>
    • 약간 삐뚤어져도 3D AI가 알아서 보정합니다! 편하게 찍으세요.
</div>
""", unsafe_allow_html=True)

camera_photo = st.camera_input("📷 모바일 정면 카메라")
uploaded_file = st.file_uploader("📂 갤러리에서 업로드", type=["jpg", "jpeg", "png"])
image_source = camera_photo if camera_photo else uploaded_file

if image_source is not None:
    image = Image.open(image_source).convert('RGB')
    image_np = np.array(image)
    
    with st.spinner("AI 3D 랜드마크 분석 중..."):
        annotated_img, metrics, error_msg = analyze_face(image_np)
    
    if error_msg:
        st.error(error_msg)
    elif metrics:
        tab1, tab2, tab3 = st.tabs(["📊 구조 분석", "🎯 심리 프로필", "📝 종합 평가"])
        
        with tab1:
            st.image(annotated_img, use_container_width=True)
            st.markdown(f"""
            <div class="metric-row"><span>BIO-HASH ID</span> <span><b>{metrics['hash']}</b></span></div>
            <div class="metric-row"><span>fWHR (골격비)</span> <span><b>{metrics['fwhr']:.2f}</b> (표준 1.7-1.9)</span></div>
            <div class="metric-row"><span>IP Index (수평비)</span> <span><b>{metrics['ip_index']:.1f}%</b> (표준 46.0%)</span></div>
            <div class="metric-row"><span>Mid-face (수직비)</span> <span><b>{metrics['mf_index']:.1f}%</b> (표준 36.0%)</span></div>
            """, unsafe_allow_html=True)
            
        with tab2:
            categories = list(metrics['scores'].keys())
            values = list(metrics['scores'].values())
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(r=values + [values[0]], theta=categories + [categories[0]], fill='toself', line_color='black', fillcolor='rgba(100,100,100,0.3)'))
            fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False, margin=dict(l=40, r=40, t=20, b=20))
            st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True})
            
        with tab3:
            comp, dom, trt = metrics['scores']['Competence'], metrics['scores']['Dominance'], metrics['scores']['Trust']
            neo = metrics['scores']['Neoteny']
            
            eval_html = "<div class='highlight-box'><ul>"
            if comp > 70 and neo < 50:
                eval_html += "<li><b>[Professional]:</b> 성숙한 비율과 대칭성이 결합되어 고도의 <b>'유능함(Competence)'</b>을 발산합니다. 일 처리가 뛰어난 전문가의 인상입니다.</li>"
            elif neo > 70 and trt > 60:
                eval_html += "<li><b>[Approachable]:</b> 타인의 경계심을 즉각적으로 낮추는 <b>'친화적 아우라'</b>가 돋보입니다. 대중에게 다가가기 쉬운 호감형입니다.</li>"
            else:
                eval_html += "<li><b>[Balanced]:</b> 안정적인 비율을 지녔습니다. 튀지 않고 편안한 <b>'신뢰감(Trustworthiness)'</b>을 주는 조화로운 인상입니다.</li>"
                
            if dom > 65:
                eval_html += "<li><b>[Authoritative]:</b> 하악각이 발달하여 공간을 장악하는 <b>'카리스마(Dominance)'</b>가 있습니다. 추진력과 결단력이 필요한 상황에 유리합니다.</li>"
            else:
                eval_html += "<li><b>[Egalitarian]:</b> 위압적이기보다 <b>수평적이고 민주적인 소통</b>을 선호하는 사람으로 인식됩니다. 훌륭한 중재자입니다.</li>"
            eval_html += "</ul></div>"
            st.markdown(eval_html, unsafe_allow_html=True)
