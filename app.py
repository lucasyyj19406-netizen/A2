import streamlit as st
import pandas as pd
from io import BytesIO

# ====================== PDF 相關套件 ======================
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

# 註冊中文字型
pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))

# ====================== Excel 匯出 ======================
def export_roster_to_excel(roster_df: pd.DataFrame):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        roster_df.to_excel(writer, index=False, sheet_name='值勤表')
    excel_data = output.getvalue()
    
    st.download_button(
        label="📥 下載 Excel 值勤表",
        data=excel_data,
        file_name="值勤排班表.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="excel_download"
    )

# ====================== PDF 匯出 ======================
def generate_prefect_roster_pdf(roster_data):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4, 
        rightMargin=36, 
        leftMargin=36, 
        topMargin=50, 
        bottomMargin=36
    )
    
    story = []
    
    title_style = ParagraphStyle(
        name='RosterTitle',
        fontName='STSong-Light',
        fontSize=18,
        leading=24,
        alignment=1,
        textColor=colors.HexColor('#1A365D')
    )
    
    cell_style = ParagraphStyle(
        name='RosterCell',
        fontName='STSong-Light',
        fontSize=10,
        leading=14,
        alignment=1,
        spaceAfter=6
    )
    
    story.append(Paragraph("學校風紀隊伍週一至週六值勤排班表", title_style))
    story.append(Spacer(1, 25))
    
    headers = ["值勤星期", "值勤隊伍", "執勤時間"]
    table_data = [[Paragraph(h, cell_style) for h in headers]]
    
    for row in roster_data:
        table_data.append([
            Paragraph(str(row.get('day', '')), cell_style),
            Paragraph(str(row.get('team', '')), cell_style),
            Paragraph(str(row.get('time', '')), cell_style)
        ])
    
    col_widths = [90, 170, 220]
    roster_table = Table(table_data, colWidths=col_widths, repeatRows=1)
    
    roster_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1A365D')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'STSong-Light'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'STSong-Light'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(roster_table)
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# ====================== 主程式 ======================
st.set_page_config(page_title="值勤排班表", layout="centered")
st.title("🛡️ 學校風紀隊 值勤排班表")
st.markdown("### 輕鬆產生 Excel 與 PDF 值勤表")

# 側邊欄輸入資料
with st.sidebar:
    st.header("📝 新增值勤資料")
    
    day = st.selectbox("值勤星期", ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六"])
    team = st.text_input("值勤隊伍", placeholder="例如：第一中隊")
    time = st.text_input("執勤時間", placeholder="例如：07:00 - 08:00")
    
    if st.button("➕ 新增至排班表"):
        if 'roster_list' not in st.session_state:
            st.session_state.roster_list = []
        st.session_state.roster_list.append({"day": day, "team": team, "time": time})
        st.success("已新增！")

# 主畫面顯示表格
if 'roster_list' not in st.session_state:
    st.session_state.roster_list = []

if st.session_state.roster_list:
    df = pd.DataFrame(st.session_state.roster_list)
    st.dataframe(df, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 生成 Excel 檔案", type="primary"):
            export_roster_to_excel(df)
    
    with col2:
        if st.button("📄 生成 PDF 檔案", type="primary"):
            pdf_bytes = generate_prefect_roster_pdf(st.session_state.roster_list)
            st.download_button(
                label="📥 下載 PDF",
                data=pdf_bytes,
                file_name="值勤排班表.pdf",
                mime="application/pdf"
            )
    
    if st.button("🗑️ 清空所有資料"):
        st.session_state.roster_list = []
        st.rerun()
else:
    st.info("👈 請在左側欄位新增值勤資料")

st.caption("使用 reportlab + Streamlit 開發 | 中文字型支援")