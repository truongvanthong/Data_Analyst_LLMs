import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from langchain_experimental.agents.agent_toolkits.pandas.base import create_pandas_dataframe_agent

from src.logger.base import BaseLogger
from src.models.llms import load_llm
from src.utils import execute_plt_code


# ----- LOAD ENV & LOGGERS -----
load_dotenv()
logger = BaseLogger()

MODEL_NAME = "gpt-3.5-turbo"
# MODEL_NAME = "gemini-1.5-pro-latest"


def process_query(da_agent, query):
    """Xử lý truy vấn người dùng và hiển thị kết quả (có thể kèm biểu đồ)."""
    # response = da_agent.invoke(query)
    response = da_agent(query)

    # Lấy intermediate_steps
    intermediate_steps = response.get("intermediate_steps", [])
    action = None

    if intermediate_steps:
        last_step = intermediate_steps[-1]
        if len(last_step) > 0:
            step_detail = last_step[0]
            if hasattr(step_detail, "tool_input"):
                action = step_detail.tool_input.get("query", None)

    # Nếu detect có code plt
    if action and "plt" in action:
        # Hiển thị phần output text
        with st.chat_message("assistant"):
            st.markdown(response["output"])

        fig = execute_plt_code(action, df=st.session_state.df)
        if fig:
            st.pyplot(fig)

        # Hiển thị code đã thực thi
        with st.expander("Executed code", expanded=False):
            st.code(action, language="python")

        # Lưu vào history
        to_display_string = response["output"] + f"\n```python\n{action}\n```"
        st.session_state.history.append((query, to_display_string))
    else:
        # Không có code
        with st.chat_message("assistant"):
            st.markdown(response["output"])

        # Debug code nếu cần
        if action:
            st.write(f"**[Debug] Last step query**: {action}")

        st.session_state.history.append((query, response["output"]))


def display_chat_history():
    """Hiển thị lịch sử chat theo dạng chat messages (nếu Streamlit đủ mới)."""
    # Nếu streamlit cũ và không có st.chat_message, ta có thể dùng phương thức cũ
    for i, (q, r) in enumerate(st.session_state.history):
        with st.chat_message("user"):
            st.markdown(f"**Query {i+1}:** {q}")

        with st.chat_message("assistant"):
            st.markdown(f"**Response {i+1}:** {r}")


def main():
    # ---- PAGE CONFIG ----
    st.set_page_config(
        page_title="📊 Smart Data Analysis Tool", 
        page_icon="📊", 
        layout="centered"
    )

    # ---- HEADER ----
    st.title("📊 Smart Data Analysis Tool")
    st.write(
        """
        <div style="text-align: justify;">
            Chào mừng bạn đến với công cụ phân tích dữ liệu thông minh. 
            Bạn có thể đặt câu hỏi, yêu cầu tạo biểu đồ và nhiều tính năng khác 
            liên quan đến tập dữ liệu của mình. 
            <br><br>
            Chỉ cần tải file CSV lên, sau đó nhập câu hỏi ở ô bên dưới, 
            hệ thống sẽ tự động thực thi và đưa ra câu trả lời kèm biểu đồ (nếu cần).
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---- SIDEBAR ----
    with st.sidebar:
        st.header("Upload Dataset")
        uploaded_file = st.file_uploader("Chọn file CSV", type="csv")
        st.write("---")
        st.markdown(
            """
            **Hướng dẫn**  
            - Tải file CSV có dữ liệu bạn cần phân tích.  
            - Nhập câu hỏi hoặc yêu cầu tính toán, tạo biểu đồ.  
            - Ví dụ: *Plot bar chart so sánh doanh thu theo tháng.*  
            """
        )

    # ---- LLM LOADING ----
    llm = load_llm(model_name=MODEL_NAME)
    logger.info(f"### Successfully loaded {MODEL_NAME} !###")

    # Khởi tạo biến history nếu chưa có
    if "history" not in st.session_state:
        st.session_state.history = []

    # Nếu đã upload file
    if uploaded_file is not None:
        st.session_state.df = pd.read_csv(uploaded_file)

        # Hiển thị một vài dòng đầu của data
        st.subheader("Preview your Data")
        st.dataframe(st.session_state.df.head(10), use_container_width=True)

        # Tạo agent
        da_agent = create_pandas_dataframe_agent(
            llm=llm,
            df=st.session_state.df,
            agent_type="tool-calling",
            allow_dangerous_code=True,
            verbose=True,
            return_intermediate_steps=True,
        )
        logger.info("### Successfully loaded data analysis agent !###")

        # Input user query
        st.markdown("### Đặt câu hỏi hoặc yêu cầu của bạn:")
        query = st.text_input(
            "E.g.: 'Hãy mô tả thống kê cơ bản của dữ liệu' hoặc 'Vẽ biểu đồ thể hiện mối quan hệ giữa các cột...'",
            placeholder="Nhập câu hỏi..."
        )

        # Nút chạy
        if st.button("Run query", type="primary"):
            if query.strip():
                with st.spinner("Processing..."):
                    # Hiển thị đoạn chat user
                    with st.chat_message("user"):
                        st.markdown(query)

                    process_query(da_agent, query)
            else:
                st.warning("Bạn chưa nhập câu hỏi nào!")

    else:
        st.info("Vui lòng tải lên một file CSV để bắt đầu.")

    # ---- Hiển thị toàn bộ lịch sử chat ----
    st.divider()
    st.subheader("Chat History")
    display_chat_history()


if __name__ == "__main__":
    main()
