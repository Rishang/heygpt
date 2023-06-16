import streamlit as st
from heygpt.core import completion_openai_gpt, completion_bard
from heygpt.serve_prompts import prompts_title


def local_css(file_name="", style=""):
    if file_name != "":
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.markdown(f"<style>{style}</style>", unsafe_allow_html=True)


st.set_page_config(
    page_title="HeyGPT",
    page_icon=":shark:",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.write("<h5 style='text-align: center'>HeyGPT</h5><br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([2, 5, 1])

with st.container():
    col4, col5, col6 = st.columns([2, 5, 1])
    with col5:
        ask = st.text_area("**Input**:", height=80)
        print_prompt = st.empty()
    with col6:
        st.write("<br><br><br>", unsafe_allow_html=True)
        submit = st.button("Submit")


with col1:
    use_bard = st.checkbox("Ask Bard", value=False)
    prompt = st.radio(
        label="**Promots**", options=["None"] + list(prompts_title.keys())
    )


with st.container():
    content = ""

    with col2:
        if prompt != "None":
            _selected_prompt = prompts_title[prompt]
            print_prompt.write(f"**Selected**: {_selected_prompt}")
        else:
            _selected_prompt = ""

        if submit:
            if not use_bard:
                completion = completion_openai_gpt(command=_selected_prompt, text=ask)
            else:
                completion = completion_bard(command=_selected_prompt, text=ask)
            content = completion
            st.markdown(content)

    with col3:
        if content != "":
            st.download_button(
                label="Download text",
                data=content.encode("utf-8"),
                file_name="output.txt",
                mime="text/html",
            )
