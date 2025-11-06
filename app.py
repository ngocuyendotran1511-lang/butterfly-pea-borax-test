import streamlit as st
from PIL import Image
import numpy as np
import os

# -----------------------------
# Cấu hình trang
# -----------------------------
st.set_page_config(page_title="Test Kit Hoa Đậu Biếc - Phát hiện hàn the", page_icon="🌸")
st.title("🌸 Test Kit Hoa Đậu Biếc Phát Hiện Hàn The (Borax)")
st.write("Ứng dụng này giúp phát hiện và ước lượng nồng độ hàn the (borax) dựa trên màu của dung dịch hoa đậu biếc so với các mẫu chuẩn đã hiệu chỉnh.")

# -----------------------------
# MỤC 1: Chọn ảnh mẫu thử
# -----------------------------
st.subheader("📷 Chụp ảnh hoặc tải ảnh mẫu thử:")

mode = st.radio("Chọn phương thức nhập ảnh:", ["📸 Chụp bằng camera", "📂 Tải ảnh từ thiết bị"])

if mode == "📸 Chụp bằng camera":
    uploaded = st.camera_input("Chụp ảnh mẫu thử:")
else:
    uploaded = st.file_uploader("Tải ảnh mẫu thử:", type=["jpg", "jpeg", "png", "gif"])

# -----------------------------
# MỤC 2: Ảnh mẫu chuẩn
# -----------------------------
st.divider()
st.subheader("🎨 Ảnh mẫu chuẩn (chuẩn hóa từ thực nghiệm)")

# Giả sử bạn đã có 5 file mẫu chuẩn đặt cùng thư mục với app.py
sample_names = ["0M", "0.001M", "0.01M", "0.1M", "1M"]
samples = {}

for name in sample_names:
    filename = f"mẫu {name}.GIF"
    if os.path.exists(filename):
        img = Image.open(filename).convert("RGB")
        samples[name] = np.array(img)
        st.image(img, caption=f"Mẫu {name}", width=120)

# -----------------------------
# Hàm tính trung bình RGB
# -----------------------------
def mean_rgb(arr):
    return np.mean(arr[:, :, 0]), np.mean(arr[:, :, 1]), np.mean(arr[:, :, 2])

# Tính trung bình RGB cho từng mẫu chuẩn
sample_colors = {}
for name, arr in samples.items():
    r, g, b = mean_rgb(arr)
    sample_colors[name] = np.array([r, g, b])

# -----------------------------
# MỤC 3: Phân tích mẫu người dùng
# -----------------------------
if uploaded:
    img = Image.open(uploaded).convert("RGB")
    st.image(img, caption="Ảnh mẫu thử", use_column_width=True)
    arr = np.array(img)

    r, g, b = mean_rgb(arr)
    sample_rgb = np.array([r, g, b])
    st.write(f"📊 Giá trị trung bình RGB: R={r:.1f}, G={g:.1f}, B={b:.1f}")

    # -----------------------------
    # So sánh với mẫu chuẩn (tính khoảng cách màu)
    # -----------------------------
    closest_name = None
    min_dist = float("inf")

    for name, ref_rgb in sample_colors.items():
        dist = np.linalg.norm(sample_rgb - ref_rgb)
        if dist < min_dist:
            min_dist = dist
            closest_name = name

    # -----------------------------
    # Kết quả suy luận
    # -----------------------------
    if closest_name == "0M":
        result = "✅ Không phát hiện hàn the (Âm tính)"
        concentration = 0
        color = "green"
    elif closest_name == "0.001M":
        result = "⚠️ Dấu hiệu hàn the rất nhẹ (~10–30 mg/L)"
        concentration = 20
        color = "orange"
    elif closest_name == "0.01M":
        result = "⚠️ Có hàn the mức trung bình (~50–80 mg/L)"
        concentration = 65
        color = "orange"
    elif closest_name == "0.1M":
        result = "❗ Có hàn the cao (~100–200 mg/L)"
        concentration = 150
        color = "red"
    else:
        result = "🚨 Hàm lượng hàn the rất cao (>200 mg/L)"
        concentration = 250
        color = "darkred"

    st.markdown(f"<h3 style='color:{color}'>{result}</h3>", unsafe_allow_html=True)
    st.write(f"🎯 Mẫu này gần giống với **mẫu chuẩn {closest_name}** (khoảng cách màu = {min_dist:.1f})")
    st.progress(min(concentration, 250) / 250)
    st.write(f"💧 Ước lượng nồng độ hàn the: **~{concentration} mg/L**")

    st.caption("📌 Kết quả chỉ mang tính tham khảo định tính, cần xác nhận lại bằng phương pháp chuẩn hóa trong phòng thí nghiệm.")
else:
    st.info("Vui lòng chụp hoặc tải ảnh mẫu thử để bắt đầu phân tích.")
