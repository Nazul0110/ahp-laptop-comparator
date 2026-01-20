import streamlit as st

def sidebar_header():
    st.sidebar.markdown(
        '<div style="font-size:22px;font-weight:800;color:#e9ecff;line-height:1.1;">🧠 AHP Laptop<br>Comparator PRO</div>',
        unsafe_allow_html=True
    )
    st.sidebar.markdown(
        '<div style="color:rgba(233,236,255,.72);font-size:13px;margin-top:6px;margin-bottom:8px;">'
        'Metode AHP • Multi-skenario • Report PDF</div>',
        unsafe_allow_html=True
    )

def inject_sidebar_css():
    st.markdown(r"""
    <style>
    [data-testid="stSidebar"] {
        background: radial-gradient(1200px 600px at 40% 10%, rgba(120,80,255,.35), transparent 60%),
                    linear-gradient(180deg, #0b1020 0%, #070a14 100%);
        border-right: 1px solid rgba(255,255,255,.06);
    }
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 18px;
        padding-left: 14px;
        padding-right: 14px;
    }
    [data-testid="stSidebar"] [data-baseweb="select"] > div {
        border-radius: 14px !important;
        background: rgba(255,255,255,.06) !important;
        border: 1px solid rgba(255,255,255,.10) !important;
        box-shadow: 0 10px 25px rgba(0,0,0,.28);
    }
    [data-testid="stSidebar"] [data-baseweb="select"] * { color: #e9ecff !important; }
    [data-testid="stSidebar"] button {
        border-radius: 14px !important;
        background: rgba(255,255,255,.06) !important;
        border: 1px solid rgba(255,255,255,.12) !important;
        color: #e9ecff !important;
        box-shadow: 0 10px 25px rgba(0,0,0,.28);
    }
    [data-testid="stSidebar"] button:hover{
        border-color: rgba(160,140,255,.55) !important;
        background: rgba(255,255,255,.08) !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child{ display:none !important; }
    [data-testid="stSidebar"] div[role="radiogroup"] label{
        width: 100%;
        background: rgba(255,255,255,.05);
        border: 1px solid rgba(255,255,255,.10);
        border-radius: 16px;
        padding: 14px 14px;
        margin: 10px 0;
        box-shadow: 0 14px 30px rgba(0,0,0,.30);
        transition: all .18s ease;
        position: relative;
        cursor: pointer;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label:hover{
        transform: translateY(-1px);
        border-color: rgba(160,140,255,.55);
        background: rgba(255,255,255,.07);
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label p{
        font-size: 15px !important;
        font-weight: 650 !important;
        color: rgba(233,236,255,.92) !important;
        margin: 0 !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label:has(div[aria-checked="true"]) {
        background: linear-gradient(180deg, rgba(120,80,255,.22), rgba(255,255,255,.06));
        border-color: rgba(120,80,255,.55);
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label:has(div[aria-checked="true"])::before{
        content:"";
        width: 9px;
        height: 9px;
        border-radius: 99px;
        background: #2ee59d;
        position:absolute;
        left: 14px;
        top: 50%;
        transform: translateY(-50%);
        box-shadow: 0 0 0 3px rgba(46,229,157,.12);
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label:has(div[aria-checked="true"]) p{
        padding-left: 18px !important;
    }
    </style>
    """, unsafe_allow_html=True)
