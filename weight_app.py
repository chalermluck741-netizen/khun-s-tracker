import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import os
from datetime import datetime
from PIL import Image

# ตั้งค่าฟอนต์สากลเพื่อป้องกันกรอบสี่เหลี่ยมพังบนอินเทอร์เน็ต
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.unicode_minus'] = False

st.set_page_config(page_title="Weight & Photo Loss Tracker", layout="centered")

# หัวข้อหลักภาษาไทยโฉมใหม่ของคุณเอส
st.title("🏃‍♂️ โปรแกรมติดตามน้ำหนัก คุณ เอส")
st.write("เป้าหมายลดน้ำหนักจาก 102 kg สู่ 90 kg เพื่อสุขภาพที่ดีขึ้น!")

START_WEIGHT = 102.0
TARGET_WEIGHT = 90.0
FILE_NAME = "weight_history.csv"
IMAGE_DIR = "weight_photos"

# สร้างโฟลเดอร์สำหรับเก็บรูปภาพถ้ายังไม่มี
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

# ฟังก์ชันสำหรับโหลดข้อมูล
def load_data():
    if os.path.exists(FILE_NAME):
        try:
            return pd.read_csv(FILE_NAME)
        except:
            pass
    
    initial_data = {
        "วันที่": [datetime.now().strftime("%Y-%m-%d")],
        "น้ำหนัก (kg)": [START_WEIGHT],
        "ชื่อรูปภาพ": ["none"]
    }
    df = pd.DataFrame(initial_data)
    df.to_csv(FILE_NAME, index=False)
    return df

df = load_data()

# ตรวจสอบความสมบูรณ์ของตารางข้อมูล
if "ชื่อรูปภาพ" not in df.columns:
    df["ชื่อรูปภาพ"] = "none"

current_weight = float(df["น้ำหนัก (kg)"].iloc[-1])

# ส่วนที่ 1: แสดงสถานะปัจจุบัน
col1, col2, col3 = st.columns(3)
lost_so_far = START_WEIGHT - current_weight
progress_percent = min(max(lost_so_far / (START_WEIGHT - TARGET_WEIGHT), 0.0), 1.0)

with col1:
    st.metric(label="น้ำหนักเริ่มต้น", value=f"{START_WEIGHT} kg")
with col2:
    st.metric(label="น้ำหนักปัจจุบัน", value=f"{current_weight} kg", delta=f"-{lost_so_far:.1f} kg" if lost_so_far >= 0 else f"+{abs(lost_so_far):.1f} kg")
with col3:
    st.metric(label="เป้าหมาย", value=f"{TARGET_WEIGHT} kg")

st.write(f"**ความคืบหน้าสู่เป้าหมาย:** {progress_percent*100:.1f}%")
st.progress(progress_percent)
st.write("---")

# ส่วนที่ 2: ฟอร์มกรอกน้ำหนักและอัปโหลดรูปถ่าย
st.subheader("📝 บันทึกประวัติประจำวัน")
date_input = st.date_input("เลือกวันที่บันทึก:", datetime.now())
new_weight = st.number_input("กรอกน้ำหนักวันนี้ (kg):", min_value=30.0, max_value=200.0, value=current_weight, step=0.1)

# ช่องอัปโหลดรูปภาพ
uploaded_file = st.file_uploader("📸 แนบรูปถ่ายหุ่นของคุณวันนี้ (ไฟล์ .jpg หรือ .png):", type=["jpg", "jpeg", "png"])

if st.button("💾 กดบันทึกข้อมูลและรูปภาพลงเครื่อง"):
    formatted_date = date_input.strftime("%Y-%m-%d")
    image_name = "none"
    
    if uploaded_file is not None:
        image_name = f"img_{formatted_date}.png"
        img_path = os.path.join(IMAGE_DIR, image_name)
        image = Image.open(uploaded_file)
        image.save(img_path)
    
    if formatted_date in df["วันที่"].values:
        df.loc[df["วันที่"] == formatted_date, "น้ำหนัก (kg)"] = new_weight
        if image_name != "none":
            df.loc[df["วันที่"] == formatted_date, "ชื่อรูปภาพ"] = image_name
    else:
        new_row = pd.DataFrame({"วันที่": [formatted_date], "น้ำหนัก (kg)": [new_weight], "ชื่อรูปภาพ": [image_name]})
        df = pd.concat([df, new_row], ignore_index=True)
        
    df.to_csv(FILE_NAME, index=False)
    st.success(f"บันทึกน้ำหนัก {new_weight} kg และรูปถ่ายเรียบร้อยแล้ว!")
    st.rerun()

st.write("---")

# ส่วนที่ 3: Photo Trend
st.subheader("🖼️ Photo Trend (เปรียบเทียบพัฒนาการหุ่น)")
images_with_photos = df[df["ชื่อรูปภาพ"].notna() & (df["ชื่อรูปภาพ"] != "none") & (df["ชื่อรูปภาพ"] != "")]

if len(images_with_photos) >= 2:
    col_old, col_new = st.columns(2)
    
    # รูปวันแรกสุด
    oldest_row = images_with_photos.iloc[0]
    old_img_path = os.path.join(IMAGE_DIR, oldest_row["ชื่อรูปภาพ"])
    if os.path.exists(old_img_path):
        with col_old:
            st.image(old_img_path, caption=f"First Day ({oldest_row['วันที่']}) | {oldest_row['น้ำหนัก (kg)']} kg", use_container_width=True)
            
    # รูปปัจจุบันล่าสุด
    newest_row = images_with_photos.iloc[-1]
    new_img_path = os.path.join(IMAGE_DIR, newest_row["ชื่อรูปภาพ"])
    if os.path.exists(new_img_path):
        with col_new:
            st.image(new_img_path, caption=f"Latest Day ({newest_row['วันที่']}) | {newest_row['น้ำหนัก (kg)']} kg", use_container_width=True)
else:
    st.info("💡 เมื่อคุณอัปโหลดรูปภาพสะสมตั้งแต่ 2 วันขึ้นไป ระบบจะดึงรูปวันแรกและวันล่าสุดมาเปรียบเทียบความฟิตให้ตรงนี้อัตโนมัติครับ!")

st.write("---")

# ส่วนที่ 4: แสดงกราฟแนวโน้มน้ำหนัก (ปรับคำเป็นภาษาอังกฤษเพื่อแก้ปัญหากรอบสี่เหลี่ยมพัง)
st.subheader("📈 กราฟแสดงแนวโน้มน้ำหนัก")
if len(df) > 0:
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(df["วันที่"], df["น้ำหนัก (kg)"], marker='o', color='#FF4B4B', linewidth=2, label="Your Weight")
    ax.axhline(y=TARGET_WEIGHT, color='green', linestyle='--', label="Target (90 kg)")
    ax.set_ylabel("Weight (kg)")
    plt.xticks(rotation=45)
    ax.grid(axis='y', linestyle=':', alpha=0.6)
    ax.legend()
    st.pyplot(fig)

st.subheader("📋 ประวัติการบันทึกทั้งหมด")
st.dataframe(df, use_container_width=True)
