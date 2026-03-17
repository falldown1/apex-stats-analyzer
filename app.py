import streamlit as st
from PIL import Image
import pytesseract
import pandas as pd
import re


# ==========================================
# 1. 配置与 OCR 函数 (复用你的逻辑)
# ==========================================
def get_number_from_roi(image, roi):
    cropped_img = image.crop(roi)
    gray_img = cropped_img.convert('L')
    width, height = gray_img.size
    resized_img = gray_img.resize((width * 2, height * 2), Image.Resampling.LANCZOS)

    config = '--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789'
    text = pytesseract.image_to_string(resized_img, config=config).strip()
    clean_text = re.sub(r'\D', '', text)
    return int(clean_text) if clean_text else 0


# ==========================================
# 2. 软件界面设计 (Streamlit)
# ==========================================

st.set_page_config(page_title="Apex 战绩自动化分析工具", layout="centered")

st.title("🎮 Apex 战绩识别软件")
st.write("上传结算截图，自动提取数据并计算 D/K 比")

# 2.1 文件上传器
uploaded_file = st.file_uploader("点击或拖拽上传战绩截图 (PNG/JPG)", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # 展示上传的图片
    img = Image.open(uploaded_file)
    st.image(img, caption='已上传的图片', use_container_width=True)

    # 坐标设置
    rois = {
        "击杀": (1744, 81, 1766, 102),
        "助攻": (1817, 81, 1836, 102),
        "老板分": (1890, 81, 1915, 102),
        "伤害": (2001, 81, 2050, 102)
    }

    # 2.2 开始识别
    if st.button("开始自动识别"):
        with st.spinner('正在分析图片，请稍候...'):
            match_result = {}
            for stat_name, coords in rois.items():
                match_result[stat_name] = get_number_from_roi(img, coords)

            # 转为 Pandas DataFrame
            df = pd.DataFrame([match_result])

            # ==========================================
            # 3. 结果展示
            # ==========================================
            st.success("识别完成！")

            # 用美观的 Metric 瓷砖显示数据
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("击杀", match_result["击杀"])
            col2.metric("助攻", match_result["助攻"])
            col3.metric("老板分", match_result["老板分"])
            col4.metric("伤害", match_result["伤害"])

            # 3.1 核心数据计算：D/K 比
            st.divider()
            st.subheader("📊 深度分析")

            damage = df['伤害'].iloc[0]
            kills = df['击杀'].iloc[0]

            if kills > 0:
                dk_ratio = damage / kills
                # 用大幅字显示 D/K
                st.metric(label="D/K (每击杀贡献伤害)", value=f"{dk_ratio:.2f}")

                # 经济学/统计学视角的简单评价
                if dk_ratio > 1000:
                    st.warning("这把 D/K 极高！你可能在远程‘抽奖’，或者全是‘残血人头’。")
                elif dk_ratio < 200:
                    st.info("这把 D/K 较低，你是个‘收割机器’，人头拿得很稳！")
            else:
                st.error("这把没有击杀，无法计算 D/K 比。")

            # 展示原始 DataFrame 表格
            st.write("原始数据表：")
            st.dataframe(df, use_container_width=True)