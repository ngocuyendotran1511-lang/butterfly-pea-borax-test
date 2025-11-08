import streamlit as st
from PIL import Image
import numpy as np
import os

st.set_page_config(page_title="Test Kit Hoa Đậu Biếc - Phát hiện hàn the", page_icon="🌸", layout="centered")

st.title("🌸 Test Kit Hoa Đậu Biếc — Phát hiện & Ước lượng Hàn The")
st.write("Chụp hoặc tải ảnh que thử (hoa đậu biếc). Ứng dụng sẽ so sánh màu và ước lượng nồng độ hàn the (mg/L).")

# -------------------------
# Hàm tiện ích
# -------------------------
def mean_rgb_from_img_pil(img_pil):
    arr = np.array(img_pil.convert("RGB"))
    r, g, b = np.mean(arr[:, :, 0]), np.mean(arr[:, :, 1]), np.mean(arr[:, :, 2])
    return np.array([r, g, b])

def try_load_image_mean(path):
    if os.path.exists(path):
        try:
            im = Image.open(path).convert("RGB")
            return mean_rgb_from_img_pil(im)
        except Exception as e:
            return None
    return None

def euclidean(a, b):
    return np.linalg.norm(a - b)

# -------------------------
# 1) Tạo màu chuẩn âm từ 2 file mẫu âm bạn đã cung cấp
# -------------------------
neg_files = ["mẫu âm.GIF", "MẪU ÂM 2.GIF"]  # tên file chính xác như bạn đã tải lên repo
neg_colors = []
for f in neg_files:
    c = try_load_image_mean(f)
    if c is not None:
        neg_colors.append(c)

if len(neg_colors) == 0:
    st.warning("Không tìm thấy file mẫu âm trong repo (mẫu âm.GIF, MẪU ÂM 2.GIF). Vui lòng upload để có hiệu chuẩn chính xác.")
    # fallback default negative color (tím nhạt) - chỉ để app chạy
    negative_color = np.array([110.0, 90.0, 140.0])
else:
    negative_color = np.mean(np.stack(neg_colors, axis=0), axis=0)

# -------------------------
# 2) Các mẫu chuẩn khác (cố gắng tải file nếu có, nếu không dùng giá trị mặc định)
# -------------------------
# mapping name -> (file name, concentration mg/L, fallback_rgb)
standard_defs = {
    "0.01M": ("mẫu 0.01M.GIF", 65, np.array([85.0, 100.0, 145.0])),
    "0.1M":  ("mẫu 0.1M.GIF", 150, np.array([80.0, 110.0, 155.0])),
    "1M":    ("mẫu 1M.GIF", 250, np.array([75.0, 120.0, 165.0])),
}

standard_colors = {}
for label, (fname, conc, fallback) in standard_defs.items():
    c = try_load_image_mean(fname)
    if c is None:
        # dùng fallback nhưng thông báo
        standard_colors[label] = {"rgb": fallback, "conc": conc, "source": "fallback"}
    else:
        standard_colors[label] = {"rgb": c, "conc": conc, "source": fname}

# Negative control entry
standard_colors["0M_negative_control"] = {"rgb": negative_color, "conc": 0, "source": "mẫu âm (tính trung bình)"}

# -------------------------
# UI: upload / camera
# -------------------------
st.subheader("📷 Chụp ảnh hoặc tải ảnh que thử")
choice = st.radio("Chọn cách nhập ảnh:", ["📸 Chụp bằng camera", "📂 Tải ảnh từ thiết bị"], index=0)
if choice.startswith("📸"):
    uploaded = st.camera_input("Chụp ảnh que thử")
else:
    uploaded = st.file_uploader("Tải ảnh que thử (jpg/png/gif)", type=["jpg", "jpeg", "png", "gif"])

if uploaded is None:
    st.info("Vui lòng chụp hoặc tải ảnh để bắt đầu phân tích.")
    st.write("Gợi ý: chụp trong hộp chụp/ánh sáng trắng, nền trắng, giữ que thẳng và chiếm phần chính khung hình.")
    # show note about standard sources
    st.write("---")
    st.write("**Thông tin chuẩn:**")
    for k, v in standard_colors.items():
        st.write(f"- {k}: source = {v['source']}, concentration ≈ {v['conc']} mg/L")
else:
    # load PIL image
    img = Image.open(uploaded).convert("RGB")
    st.image(img, caption="Ảnh mẫu thử", use_column_width=True)
    sample_rgb = mean_rgb_from_img_pil(img)
    st.write(f"🔹 Giá trị trung bình RGB: **R={sample_rgb[0]:.0f}, G={sample_rgb[1]:.0f}, B={sample_rgb[2]:.0f}**")

    # show block of average color
    hexcol = '#%02x%02x%02x' % (int(sample_rgb[0]), int(sample_rgb[1]), int(sample_rgb[2]))
    st.markdown(f"<div style='height:48px; border-radius:6px; background:{hexcol}; text-align:center; line-height:48px; color:#fff;'>🎨 Màu trung bình</div>", unsafe_allow_html=True)

    # -------------------------
    # So sánh với tất cả chuẩn
    # -------------------------
    best_label = None
    best_dist = float("inf")
    for label, meta in standard_colors.items():
        dist = euclidean(sample_rgb, meta["rgb"])
        if dist < best_dist:
            best_dist = dist
            best_label = label

    best_meta = standard_colors[best_label]
    conc_est = best_meta["conc"]
    source = best_meta["source"]

    # -------------------------
    # Quy tắc hiển thị kết quả
    # -------------------------
    if conc_est == 0:
        status = "✅ Không phát hiện hàn the (âm tính)"
        badge_color = "#2ecc71"
        guidance = "Mẫu nằm trong vùng âm tính."
    elif conc_est <= 80:
        status = "⚠️ Dấu hiệu hàn the nhẹ (~vết)"
        badge_color = "#f1c40f"
        guidance = "Cần thận trọng; nếu cần, tiến hành kiểm tra bằng phương pháp chuẩn."
    elif conc_est <= 200:
        status = "❗ Có hàn the (mức trung bình/không an toàn)"
        badge_color = "#e67e22"
        guidance = "Không tiêu thụ. Khuyến nghị xác minh bằng phòng thí nghiệm."
    else:
        status = "🚨 Hàm lượng rất cao (nguy hiểm)"
        badge_color = "#e74c3c"
        guidance = "Ngưng sử dụng sản phẩm ngay lập tức và báo cơ quan chức năng."

    # hiển thị
    st.markdown(f"<div style='padding:16px; border-radius:12px; background:{badge_color}22;'><h3 style='color:{badge_color}; text-align:center;'>{status}</h3><p style='text-align:center;color:#333;'>{guidance}</p></div>", unsafe_allow_html=True)
    st.write(f"📌 Mẫu gần giống: **{best_label}** (nguồn: {source}) — khoảng cách màu = {best_dist:.1f}")
    st.write(f"💧 Ước lượng nồng độ tương đương: **~{conc_est} mg/L**")

    # progress bar visual
    st.progress(min(conc_est, 300) / 300)

    st.caption("🔎 Ghi chú: Kết quả mang tính sàng lọc, tham khảo. Để kết luận chính thức cần phân tích phòng thí nghiệm (phương pháp chuẩn).")

    # show debug option to display all distances (hidden by default)
    if st.checkbox("Hiển thị chi tiết khoảng cách màu (debug)"):
        for label, meta in standard_colors.items():
            st.write(f"- {label}: RGB={np.round(meta['rgb'],1)} ; dist = {euclidean(sample_rgb, meta['rgb']):.1f} ; source={meta['source']}")
