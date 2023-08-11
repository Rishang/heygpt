import streamlit as st
from heygpt.core import completion_openai_gpt, completion_palm_text, openai_model
from heygpt.serve_prompts import prompts_title
from heygpt.utils import log


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

col1, col2, col3 = st.columns([2, 5, 1])

with st.container():
    col4, col5, col6 = st.columns([2, 5, 1])
    with col2:
        ask = st.text_area("**Input**:", height=80)
        print_prompt = st.empty()
    with col3:
        st.write("<br><br><br>", unsafe_allow_html=True)
        submit = st.button("Submit")


with col1:
    _options = {
        f"{openai_model.upper()}": f"{openai_model}",
        "Davinci": "text-davinci-003",
        "Palm": "palm",
    }
    use_model = st.radio("**Model**", options=_options.keys())
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
            if use_model != "Palm":
                completion = completion_openai_gpt(
                    command=_selected_prompt, text=ask, model=_options[use_model]
                )
                if "davinci" in use_model.lower():
                    st.markdown(f"```{completion}")
                else:
                    st.markdown(completion)

            else:
                completion = completion_palm_text(command=_selected_prompt, text=ask)
                st.markdown(completion)

            content = completion

    with col3:
        if content != "":
            st.download_button(
                label="Download text",
                data=content.encode("utf-8"),
                file_name="output.txt",
                mime="text/html",
            )
