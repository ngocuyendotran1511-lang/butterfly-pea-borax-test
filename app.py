import streamlit as st
from PIL import Image
import numpy as np
import os

# -----------------------------
# Cấu hình trang
# -----------------------------
st.set_page_config(page_title="Hoa đậu biếc phát hiện hàn the", page_icon="🌸", layout="centered")
st.title("🌸 Test Kit Hoa Đậu Biếc Phát Hiện Hàn The")
st.markdown("""
Ứng dụng giúp **phát hiện và ước lượng nồng độ hàn the (borax)** trong thực phẩm 
dựa trên màu của dung dịch **hoa đậu biếc**.  
Hãy chụp hoặc tải ảnh mẫu thử của bạn để hệ thống tự động phân tích.
""")

# -----------------------------
# MỤC 1: Chọn ảnh mẫu thử
# -----------------------------
st.subheader("📷 Chụp ảnh hoặc tải ảnh mẫu thử:")

mode = st.radio("Chọn cách nhập ảnh:", ["📸 Chụp bằng camera", "📂 Tải ảnh từ thiết bị"])

if mode == "📸 Chụp bằng camera":
    uploaded = st.camera_input("Chụp ảnh mẫu thử:")
else:
    uploaded = st.file_uploader("Tải ảnh mẫu thử:", type=["jpg", "jpeg", "png", "gif"])

# -----------------------------
# MỤC 2: Ảnh mẫu chuẩn (chỉ dùng nội bộ, không hiển thị)
# -----------------------------
sample_names = ["0M", "0.001M", "0.01M", "0.1M", "1M"]
samples = {}

def mean_rgb(arr):
    return np.mean(arr[:, :, 0]), np.mean(arr[:, :, 1]), np.mean(arr[:, :, 2])

# Đọc mẫu chuẩn (đặt sẵn cùng thư mục app)
for name in sample_names:
    filename = f"mẫu {name}.GIF"
    if os.path.exists(filename):
        img = Image.open(filename).convert("RGB")
        samples[name] = np.array(img)

# Tính trung bình RGB mẫu chuẩn
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

    st.write(f"🔹 Giá trị trung bình RGB: **R={r:.0f}, G={g:.0f}, B={b:.0f}**")

    # So sánh khoảng cách màu
    closest_name = None
    min_dist = float("inf")
    for name, ref_rgb in sample_colors.items():
        dist = np.linalg.norm(sample_rgb - ref_rgb)
        if dist < min_dist:
            min_dist = dist
            closest_name = name

    # Kết quả phân tích
    if closest_name == "0M":
        result = "✅ Không phát hiện hàn the"
        concentration = 0
        color = "#2ecc71"
        icon = "🟢"
        desc = "Mẫu âm tính, an toàn."
    elif closest_name == "0.001M":
        result = "⚠️ Có dấu hiệu rất nhẹ"
        concentration = 20
        color = "#f1c40f"
        icon = "🟡"
        desc = "Có thể chứa lượng hàn the nhỏ (<30 mg/L)."
    elif closest_name == "0.01M":
        result = "⚠️ Có hàn the mức trung bình"
        concentration = 65
        color = "#e67e22"
        icon = "🟠"
        desc = "Cần kiểm tra thêm (50–80 mg/L)."
    elif closest_name == "0.1M":
        result = "❗ Hàm lượng hàn the cao"
        concentration = 150
        color = "#e74c3c"
        icon = "🔴"
        desc = "Không an toàn cho sức khỏe (100–200 mg/L)."
    else:
        result = "🚨 Hàm lượng rất cao"
        concentration = 250
        color = "#8e44ad"
        icon = "🟣"
        desc = "Vượt giới hạn an toàn (>200 mg/L)."

    # Hiển thị kết quả đẹp
    st.markdown(f"""
    <div style='background-color:{color}22; padding:20px; border-radius:15px;'>
        <h3 style='color:{color}; text-align:center;'>{icon} {result}</h3>
        <p style='text-align:center; color:#333;'>{desc}</p>
    </div>
    """, unsafe_allow_html=True)

    st.write(f"🎯 Mẫu thử gần giống với **mẫu chuẩn {closest_name}** (khoảng cách màu = {min_dist:.1f})")
    st.progress(min(concentration, 250) / 250)
    st.markdown(f"<h4 style='color:{color}; text-align:center;'>💧 Ước lượng nồng độ hàn the: ~{concentration} mg/L</h4>", unsafe_allow_html=True)

    st.caption("📌 Kết quả chỉ mang tính định tính và tham khảo. Nên kiểm tra lại bằng phương pháp chuẩn hóa trong phòng thí nghiệm.")
else:
    st.info("Vui lòng chụp hoặc tải ảnh mẫu thử để bắt đầu phân tích.")
