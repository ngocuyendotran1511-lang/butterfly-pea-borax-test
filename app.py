import streamlit as st
import cv2
import numpy as np
from PIL import Image
import os

st.set_page_config(page_title="Bộ Kit Hoa Đậu Biếc – Phát hiện Hàn The", page_icon="🧪", layout="wide")

st.title("🧪 Bộ Kit Hoa Đậu Biếc – Phát hiện và Ước lượng nồng độ Hàn The")
st.write("""
Ứng dụng sử dụng màu sắc que thử từ hoa đậu biếc để phát hiện **hàn the (borax)** trong thực phẩm.  
Người dùng chỉ cần tải ảnh que thử, hệ thống sẽ phân tích màu và ước lượng nồng độ tương ứng.
""")

# ====== DỮ LIỆU MẪU CHUẨN ======
standard_files = {
    "0M (âm tính)": "mẫu 0M.GIF",
    "0.001M (~38 mg/L)": "mẫu 0.001M.GIF",
    "0.01M (~380 mg/L)": "mẫu 0.01M.GIF",
    "0.1M (~3800 mg/L)": "mẫu 0.1M.GIF",
    "1M (~38000 mg/L)": "mẫu 1M.GIF"
}

def avg_color(path):
    img = cv2.imread(path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return np.mean(img.reshape(-1, 3), axis=0)

def color_distance(c1, c2):
    return np.sqrt(np.sum((c1 - c2) ** 2))

# ====== HIỂN THỊ MẪU CHUẨN ======
st.subheader("🎨 Màu Mẫu Chuẩn")
cols = st.columns(len(standard_files))
std_colors = {}

for i, (label, path) in enumerate(standard_files.items()):
    if os.path.exists(path):
        color = avg_color(path)
        std_colors[label] = color
        with cols[i]:
            st.image(path, caption=f"{label}\nRGB: {np.round(color,1)}", width=140)
    else:
        st.warning(f"⚠️ Không tìm thấy file {path}")

# ====== UPLOAD MẪU THỬ ======
st.subheader("📸 Phân tích mẫu thử")
uploaded = st.file_uploader("Tải ảnh que thử (JPG, PNG, GIF)", type=["jpg","jpeg","png","gif"])

if uploaded:
    img = Image.open(uploaded)
    img_np = np.array(img)
    st.image(img, caption="Ảnh mẫu thử", use_column_width=True)

    # Tính màu trung bình
    mean_color = np.mean(img_np.reshape(-1, 3), axis=0)
    st.write(f"🔹 Màu trung bình mẫu thử (RGB): {np.round(mean_color, 1)}")

    # So sánh với mẫu chuẩn
    min_dist, best_match = float("inf"), None
    for label, color in std_colors.items():
        dist = color_distance(mean_color, color)
        if dist < min_dist:
            min_dist = dist
            best_match = label

    # ====== XỬ LÝ KẾT QUẢ ======
    st.subheader("🧭 Kết quả phân tích")

    if "0M" in best_match:
        st.success("✅ Mẫu âm tính – KHÔNG phát hiện hàn the trong mẫu thực phẩm.")
        concentration = 0
    else:
        # Tách nồng độ mg/L từ chuỗi label
        concentration = float(best_match.split("~")[1].split("mg")[0].strip())
        st.warning(f"⚠️ Mẫu có khả năng chứa hàn the ở mức tương đương: **{concentration:.0f} mg/L**.")

    st.write(f"🎯 Mức tương đồng màu gần nhất: **{best_match}**")
    st.write(f"📏 Khoảng cách màu (độ sai lệch): `{min_dist:.2f}`")

    # Gợi ý kết luận định lượng
    st.subheader("📊 Đánh giá mức độ an toàn")
    if concentration == 0:
        st.write("🟢 **An toàn – không phát hiện hàn the.**")
    elif concentration < 400:
        st.write("🟡 **Có dấu hiệu rất nhỏ của hàn the – mức vết.**")
    elif concentration < 4000:
        st.write("🟠 **Hàm lượng trung bình – cần kiểm tra lại bằng thiết bị chuẩn.**")
    else:
        st.write("🔴 **Hàm lượng cao – không an toàn cho thực phẩm.**")
