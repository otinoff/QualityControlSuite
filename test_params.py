"""
Тестовый скрипт для проверки работы с query_params в Streamlit
"""

import streamlit as st

st.set_page_config(page_title="Test Params")

st.title("Тест параметров")

# Показываем текущие параметры
st.write("Текущие query_params:", dict(st.query_params))

# Тест установки параметра
if st.button("Установить report_id=test123"):
    st.query_params["report_id"] = "test123"
    st.rerun()

if st.button("Очистить параметры"):
    st.query_params.clear()
    st.rerun()

# Проверяем параметр report_id
report_id = st.query_params.get("report_id", None)
if report_id:
    st.success(f"Report ID получен: {report_id}")
else:
    st.info("Report ID не установлен")