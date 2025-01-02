import streamlit as st
from pygwalker.api.streamlit import StreamlitRenderer


def main():
    # ----- PAGE CONFIG -----
    st.set_page_config(
        page_title="📈 Interactive Visualization Tool", 
        page_icon="📈", 
        layout="wide"
    )

    # ----- HEADER -----
    st.title("📈 Interactive Visualization Tool")
    st.write(
        """
        <div style="text-align: justify;">
            Chào mừng bạn đến với công cụ trực quan dữ liệu <b>pygwalker</b>.
            Công cụ này cho phép bạn khám phá và tương tác với dữ liệu một cách thuận tiện:
            <ul>
              <li><b>Nhấp và kéo</b> để lọc dữ liệu theo điều kiện mong muốn.</li>
              <li><b>Chọn cột</b> để vẽ biểu đồ theo ý muốn (bar chart, scatter plot, line chart,...).</li>
            </ul>
            <br>
            Trước khi sử dụng, hãy chắc chắn rằng bạn đã <b>upload file CSV</b> ở trang 
            <b>📊 Smart Data Analysis Tool</b>. Sau đó quay lại đây để tận hưởng trải nghiệm trực quan hoá dữ liệu.
        </div>
        """,
        unsafe_allow_html=True
    )

    # ----- SIDEBAR (OPTIONAL) -----
    with st.sidebar:
        st.header("Cài đặt / Hướng dẫn")
        st.info(
            """
            1. Di chuyển sang trang "📊 Smart Data Analysis Tool" để tải file CSV.  
            2. Quay lại trang này, dữ liệu sẽ tự động được nạp.  
            3. Tự do khám phá và tạo biểu đồ theo ý muốn.  
            4. Bạn có thể "Kéo - Thả" cột, tạo điều kiện lọc, thêm tính năng pivot...  
            """
        )

    # ----- MAIN CONTENT -----
    # Kiểm tra xem df đã tồn tại trong session_state hay chưa
    if st.session_state.get("df") is not None:
        st.success("Dữ liệu đã sẵn sàng để khám phá với pygwalker! Hãy trải nghiệm ở bên dưới.")
        
        # Tạo và render pygwalker
        pyg_app = StreamlitRenderer(st.session_state.df)
        pyg_app.explorer()
    else:
        st.warning("Vui lòng upload một dataset ở trang '📊 Smart Data Analysis Tool' để bắt đầu!")


if __name__ == "__main__":
    main()
