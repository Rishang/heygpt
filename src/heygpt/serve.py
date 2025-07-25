import streamlit as st
import pyperclip  # type: ignore
from litellm import completion

from heygpt.core import model
from heygpt.serve_prompts import prompts_title
from heygpt.prompts import openai_fmt_prompt, configs


def local_css(file_name="", style=""):
    if file_name != "":
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.markdown(f"<style>{style}</style>", unsafe_allow_html=True)


st.set_page_config(
    page_title="HeyGPT",
    page_icon=":shark:",
    # initial_sidebar_state="collapsed",
)

# Sidebar content
_options = configs.get("available_models", [model])
# audio = st.sidebar.audio_input("Record a voice message")


def format_model_name(model_name: str) -> str:
    if model_name.startswith("openrouter/"):
        return model_name.replace("openrouter/", "", 1)
    return model_name


user_model: str = st.sidebar.selectbox(
    "**Model**", _options, format_func=format_model_name
)

prompt = st.sidebar.radio(
    label="**Promots**", options=["None"] + list(prompts_title.keys())
)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if chat_input := st.chat_input("What is up?"):
    # set stream to True if model is OpenAI
    stream = True
    if user_model.startswith("o1"):
        stream = False

    # Display user message in chat message container
    st.chat_message("user").markdown(chat_input)

    # Add user message to chat history
    if prompt == "None":
        st.session_state.messages.append({"role": "user", "content": chat_input})
    else:
        for i in openai_fmt_prompt(prompts_title[prompt]):
            print(prompt)
            st.session_state.messages.append(i)

        st.session_state.messages[-1]["content"] += f"```\n{chat_input}"

    # response = f"Echo: {prompts_title[prompt]}"
    ai_response = completion(
        model=user_model,
        messages=st.session_state.messages,
        stream=stream,
        drop_params=True,
    )

    # response = ai_response["choices"][0]["message"]["content"]
    response = []

    def stream_data():
        for part in ai_response:
            # response += part.choices[0].delta.content or ""
            # add string to response
            response.append(part.choices[0].delta.content or "")

            yield part.choices[0].delta.content or ""

    # response = ai_response["choices"][0]["message"]["content"]
    # Display assistant response in chat message container
    # stream = False
    with st.chat_message("assistant"):
        # st.markdown("\n" + response)
        if stream:
            st.write_stream(stream_data)
        else:
            #  ai_response.choices[0].delta.content or ""
            st.markdown("\n" + "".join(ai_response.choices[0].message.content or ""))
            response.append(ai_response.choices[0].message.content or "")

    # Add assistant response to chat history from the stream_data

    st.session_state.messages.append(
        {"role": "assistant", "content": "".join(response)}
    )

# Separate the "Copy to clipboard" button outside the user input block
if st.session_state.messages:
    # Create a cleaner button layout without nested columns
    button_col1, button_col2, button_col3, button_col4 = st.columns(4)

    with button_col1:
        copy_snippet = st.button("🗒️ Copy", key="copy_button")

    with button_col2:
        st.download_button(
            label="⬇️ Download",
            data=st.session_state.messages[-1]["content"],
            file_name="heygpt_output.txt",
            mime="text/text",
            key="download_button",
        )

    # Show success message in a separate container to avoid layout issues
    if copy_snippet:
        last_response = st.session_state.messages[-1]["content"]
        pyperclip.copy(last_response)
        st.success("Copied to clipboard!")
