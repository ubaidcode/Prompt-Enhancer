import time
import streamlit as st
from google import genai
from google.genai import types
from groq import Groq


# ============================================================
# PRIVATE SETTINGS
# ============================================================

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
GEMINI_MODEL = "gemini-3.5-flash"

GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
GROQ_MODEL = "openai/gpt-oss-120b"


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Prompt Enhancer",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# CUSTOM UI
# ============================================================

st.markdown("""
<style>

    .main-title {
        text-align: center;
        font-size: 38px;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        color: #777;
        font-size: 16px;
        margin-bottom: 30px;
    }

    .response-card {
        border: 1px solid rgba(128,128,128,0.25);
        border-radius: 16px;
        padding: 20px;
        min-height: 360px;
        background: rgba(128,128,128,0.04);
    }

    .card-title {
        font-size: 22px;
        font-weight: 700;
        margin-bottom: 15px;
    }

    .status {
        padding: 8px 12px;
        border-radius: 8px;
        background: rgba(128,128,128,0.08);
        margin-bottom: 12px;
    }

    .retry-box {
        text-align: center;
        padding: 15px;
        border-radius: 12px;
        background: rgba(255,165,0,0.10);
        margin-top: 10px;
    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">✨ AI Prompt Enhancer</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Write one prompt and get two enhanced versions.'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# USER PROMPT
# ============================================================

st.markdown("### ✍️ Your Prompt")

prompt = st.text_area(
    "Enter your prompt",
    placeholder="Example: Create a cinematic video of a boy walking through Karachi...",
    height=150,
    label_visibility="collapsed"
)


# ============================================================
# ENHANCEMENT INSTRUCTIONS
# ============================================================

ENHANCEMENT_INSTRUCTION = """
You are an expert prompt enhancement engine.

Your task is to transform the user's simple prompt into a
substantially better, complete and ready-to-use prompt.

IMPORTANT RULES:

- Do NOT simply repeat or lightly reword the user's prompt.
- Actually enhance the idea.
- Preserve the user's original intent.
- Make incomplete ideas complete.
- Add useful relevant details that logically improve the prompt.
- Improve clarity, specificity, structure and usefulness.
- Include relevant context, environment, actions, style,
  quality, behavior, constraints or output requirements when
  they make sense for the user's request.
- If the original prompt is extremely short, expand it properly.
- Do not invent unrelated concepts.
- Do not change the subject or intended result.
- Do not remove important information.
- Do not explain your changes.
- Do not write an introduction.
- Do not write "Here is your enhanced prompt".
- Return ONLY the final enhanced prompt.
- Keep it detailed and professional, but avoid unnecessary
  repetition or an excessively long essay.
- The final result must be directly copyable and usable.

The enhanced result should be clearly better and more complete
than the original prompt.

USER PROMPT:
"""


# ============================================================
# GENERATION FUNCTIONS
# ============================================================

def generate_gemini(user_prompt):

    client = genai.Client(
        api_key=GEMINI_API_KEY
    )

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=(
            ENHANCEMENT_INSTRUCTION
            + "\n"
            + user_prompt
        ),
        config=types.GenerateContentConfig(
            temperature=0.9,
            max_output_tokens=1200
        )
    )

    if not response.text:
        raise Exception("Gemini returned an empty response.")

    return response.text.strip()


def generate_chatgpt(user_prompt):

    client = Groq(
        api_key=GROQ_API_KEY
    )

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": ENHANCEMENT_INSTRUCTION
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        temperature=0.9,
        max_tokens=1200
    )

    answer = response.choices[0].message.content

    if not answer:
        raise Exception("ChatGPT returned an empty response.")

    return answer.strip()


# ============================================================
# RETRY FUNCTION
# ============================================================

def run_with_retry(function, user_prompt, status_box, max_attempts=2):

    last_error = None

    for attempt in range(1, max_attempts + 1):

        try:

            if attempt == 1:
                status_box.info("Responding...")

            else:
                status_box.info(
                    f"Retrying... Attempt {attempt}/{max_attempts}"
                )

            result = function(user_prompt)

            return result, None

        except Exception as error:

            last_error = error

            if attempt < max_attempts:

                for remaining in range(30, 0, -1):

                    status_box.warning(
                        f"Temporary error. Retrying in "
                        f"{remaining} seconds..."
                    )

                    time.sleep(1)

            else:

                status_box.error(
                    "Request failed after retry."
                )

    return None, last_error


# ============================================================
# GENERATE BUTTON
# ============================================================

if st.button(
    "✨ Enhance Prompt",
    type="primary",
    use_container_width=True
):

    if not prompt.strip():
        st.warning("Please enter a prompt first.")
        st.stop()

    if not GEMINI_API_KEY.strip():
        st.error("Gemini API key code ke top par add karo.")
        st.stop()

    if not GROQ_API_KEY.strip():
        st.error("Groq API key code ke top par add karo.")
        st.stop()


    st.divider()


    # ========================================================
    # TWO CLEAN RESPONSE COLUMNS
    # ========================================================

    gemini_col, chatgpt_col = st.columns(
        2,
        gap="large"
    )


    # ========================================================
    # GEMINI CARD
    # ========================================================

    with gemini_col:

        st.markdown(
            '<div class="card-title">🟢 Gemini</div>',
            unsafe_allow_html=True
        )

        gemini_status = st.empty()

        gemini_result, gemini_error = run_with_retry(
            generate_gemini,
            prompt.strip(),
            gemini_status
        )

        if gemini_result:

            gemini_status.success("Response Ready")

            st.markdown("**Enhanced Prompt**")

            st.code(
                gemini_result,
                language="text"
            )

        else:

            st.error(
                f"Gemini Error: {gemini_error}"
            )


    # ========================================================
    # CHATGPT CARD
    # ========================================================

    with chatgpt_col:

        st.markdown(
            '<div class="card-title">🔵 ChatGPT</div>',
            unsafe_allow_html=True
        )

        chatgpt_status = st.empty()

        chatgpt_result, chatgpt_error = run_with_retry(
            generate_chatgpt,
            prompt.strip(),
            chatgpt_status
        )

        if chatgpt_result:

            chatgpt_status.success("Response Ready")

            st.markdown("**Enhanced Prompt**")

            st.code(
                chatgpt_result,
                language="text"
            )

        else:

            st.error(
                f"ChatGPT Error: {chatgpt_error}"
            )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Gemini and ChatGPT generate independent enhanced versions "
    "of the same original prompt."
)