import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import os
from datetime import datetime
from PIL import Image

# ตั้งค่าฟอนต์สากลป้องกันสี่เหลี่ยมพังบนออนไลน์
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.unicode_minus'] = False

st.set_page_config(page_title="โปรแกรมติดตามน้ำหนัก", layout="centered")

st.title("🏃‍♂️ โปรแกรมติดตามน้ำหนัก คุณ เอส")
st.write("บันทึกค่าน้ำหนักประจำวัน อัปโหลดรูปภาพ และติดตามเป้าหมายของคุณ")

FILE_NAME = "weight_history.csv"
IMAGE_DIR = "weight_photos"

# สร้างโฟลเดอร์สำหรับเก็บรูปภาพถ้ายังไม่มี
if not os.path.exists(IMAGE_DIR):
    try:
        os.makedirs(IMAGE_DIR)
    except:
        pass

# ฟังก์ชันสำหรับโหลดข้อมูล (ปรับรหัสไฟล์ให้ Excel ภาษาไทยอ่านออกร้อยเปอร์เซ็นต์)
def load_data():
    if os.path.exists(FILE_NAME):
        try:
            return pd.read_csv(FILE_NAME, encoding='utf-8-sig')
        except:
            try:
                return pd.read_csv(FILE_NAME)
            except:
                pass
    
    # ข้อมูลเริ่มต้นครั้งแรกสุด
    initial_data = {
        "วันที่": [datetime.now().strftime("%Y-%m-%d")],
        "น้ำหนักปัจจุบัน": [102.0],
        "น้ำหนักเป้าหมาย": [90.0],
        "ชื่อรูปภาพ": ["none"]
    }
    df = pd.DataFrame(initial_data)
    df.to_csv(FILE_NAME, index=False, encoding='utf-8-sig')
    return df

df = load_data()

# ตรวจสอบชื่อคอลัมน์ให้ถูกต้องและเป็นระบบเดียวกันทั้งหมด
df.columns = ["วันที่", "น้ำหนักปัจจุบัน", "น้ำหนักเป้าหมาย", "ชื่อรูปภาพ"] if len(df.columns) == 4 else df.columns

last_row = df.iloc[-1]
saved_current = float(last_row["น้ำหนักปัจจุบัน"])
saved_target = float(last_row["น้ำหนักเป้าหมาย"])

st.write("---")

# ส่วนที่ 1: ฟอร์มกรอกข้อมูลตามที่คุณเอสต้องการ (น้ำหนักปัจจุบัน และ น้ำหนักเป้าหมาย)
st.subheader("📝 บันทึกข้อมูลประจำวัน")
date_input = st.date_input("เลือกวันที่บันทึก:", datetime.now())

col_input1, col_input2 = st.columns(2)
with col_input1:
    new_weight = st.number_input("กรอกน้ำหนักปัจจุบัน (kg):", min_value=30.0, max_value=200.0, value=saved_current, step=0.1)
with col_input2:
    new_target = st.number_input("กรอกน้ำหนักเป้าหมาย (kg):", min_value=30.0, max_value=200.0, value=saved_target, step=0.1)

# ช่องแนบรูปภาพถ่ายรูปร่าง
uploaded_file = st.file_uploader("📸 แนบรูปถ่ายรูปร่างของคุณวันนี้:", type=["jpg", "jpeg", "png"])

if st.button("💾 กดบันทึกข้อมูล"):
    formatted_date = date_input.strftime("%Y-%m-%d")
    image_name = "none"
    
    if uploaded_file is not None:
        image_name = f"img_{formatted_date}.png"
        try:
            img_path = os.path.join(IMAGE_DIR, image_name)
            image = Image.open(uploaded_file)
            image.save(img_path)
        except:
            image_name = "none"
    
    if formatted_date in df["วันที่"].values:
        df.loc[df["วันที่"] == formatted_date, "น้ำหนักปัจจุบัน"] = new_weight
        df.loc[df["วันที่"] == formatted_date, "น้ำหนักเป้าหมาย"] = new_target
        if image_name != "none":
            df.loc[df["วันที่"] == formatted_date, "ชื่อรูปภาพ"] = image_name
    else:
        new_row = pd.DataFrame({
            "วันที่": [formatted_date], 
            "น้ำหนักปัจจุบัน": [new_weight], 
            "น้ำหนักเป้าหมาย": [new_target], 
            "ชื่อรูปภาพ": [image_name]
        })
        df = pd.concat([df, new_row], ignore_index=True)
        
    df.to_csv(FILE_NAME, index=False, encoding='utf-8-sig')
    st.success("บันทึกข้อมูลเรียบร้อยแล้ว!")
    st.rerun()

st.write("---")

# ส่วนที่ 2: แสดงสถานะล่าสุดในปัจจุบัน
st.subheader("📊 สถานะปัจจุบัน")
col1, col2 = st.columns(2)
with col1:
    st.metric(label="น้ำหนักปัจจุบันล่าสุด", value=f"{saved_current} kg")
with col2:
    st.metric(label="น้ำหนักเป้าหมายที่ตั้งไว้", value=f"{saved_target} kg")

st.write("---")

# ส่วนที่ 3: Photo Trend เปรียบเทียบรูปร่าง อดีต-ปัจจุบัน
st.subheader("🖼️ พัฒนาการรูปร่าง (Photo Trend)")
images_with_photos = df[(df["ชื่อรูปภาพ"].notna()) & (df["ชื่อรูปภาพ"] != "none") & (df["ชื่อรูปภาพ"] != "")]

if len(images_with_photos) >= 1:
    col_old, col_new = st.columns(2)
    newest_row = images_with_photos.iloc[-1]
    
    with col_old:
        st.info("📊 พัฒนาการสัดส่วนของคุณเอส")
        if uploaded_file is not None:
            with col_new:
                st.image(uploaded_file, caption=f"รูปร่างปัจจุบันล่าสุด ({newest_row['วันที่']})", use_container_width=True)
        else:
            st.write("📸 *แนบรูปภาพด้านบนแล้วกดปุ่มบันทึก เพื่อดูรูปหุ่นเปรียบเทียบตรงนี้ได้ทันทีครับ*")
else:
    st.info("💡 แนบรูปถ่ายรูปร่างของคุณวันนี้ด้านบน เพื่อดูระบบเปรียบเทียบรูปร่างตรงนี้ได้เลยครับ")

st.write("---")

# ส่วนที่ 4: แสดงกราฟแนวโน้มน้ำหนักสากล
st.subheader("📈 กราฟแสดงแนวโน้มน้ำหนัก")
if len(df) > 0:
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(df["วันที่"], df["น้ำหนักปัจจุบัน"], marker='o', color='#FF4B4B', linewidth=2, label="Your Weight")
    ax.plot(df["วันที่"], df["น้ำหนักเป้าหมาย"], color='green', linestyle='--', label="Target Weight")
    ax.set_ylabel("Weight (kg)")
    plt.xticks(rotation=45)
    ax.grid(axis='y', linestyle=':', alpha=0.6)
    ax.legend()
    st.pyplot(fig)

st.subheader("📋 ประวัติการบันทึกทั้งหมด")
st.dataframe(df, use_container_width=True)
