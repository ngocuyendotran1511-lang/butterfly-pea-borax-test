import streamlit as st
from PIL import Image
import numpy as np

st.title("🌸 Test Kit Hoa Đậu Biếc Phát Hiện Hàn The")
st.write("Tải ảnh mẫu thử (màu dung dịch hoa đậu biếc) để phân tích cường độ màu và ước lượng nồng độ hàn the (mg/L).")

uploaded = st.file_uploader("📤 Tải ảnh mẫu thử", type=["jpg", "jpeg", "png", "gif"])

if uploaded:
    img = Image.open(uploaded)
    st.image(img, caption="Ảnh mẫu tải lên", use_column_width=True)

    # Phân tích màu
    arr = np.array(img.convert("RGB"))
    avg_r = np.mean(arr[:, :, 0])
    avg_g = np.mean(arr[:, :, 1])
    avg_b = np.mean(arr[:, :, 2])

    st.write(f"🔹 Trung bình R={avg_r:.1f}, G={avg_g:.1f}, B={avg_b:.1f}")

    # Dựa theo cường độ kênh xanh để ước lượng nồng độ
    avg_blue = avg_b

    if avg_blue < 80:
        result = "➡ Không phát hiện hàn the (0 mg/L)"
        color = "green"
    elif avg_blue < 120:
        result = "≈ 10–50 mg/L (nghi ngờ có hàn the nhẹ)"
        color = "orange"
    elif avg_blue < 160:
        result = "≈ 50–100 mg/L (có hàn the)"
        color = "orange"
    else:
        result = "⚠️ >100 mg/L – hàm lượng cao, không an toàn!"
        color = "red"

    st.markdown(f"<h3 style='color:{color}'>{result}</h3>", unsafe_allow_html=True)
