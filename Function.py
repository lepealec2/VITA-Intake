import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

import datetime
import textwrap
import streamlit as st
import os
import pickle
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders





def safe_one_line(value, max_len=120):
    """Force everything into a single safe row"""
    if isinstance(value, datetime.date):
        value = value.strftime("%Y-%m-%d")

    text = str(value)

    # HARD truncate (prevents FPDF crash)
    if len(text) > max_len:
        text = text[:max_len] + "..."

    return text



import streamlit as st
def ask_question(answers, key_name, question,index=0, input_type="text", options=None, columns=True, help_text=None, allow_none=False):
    if input_type in ["text", "text_input"]:
        answers[key_name] = st.text_input(question, key=key_name, help=help_text)

    elif input_type == "radio":
        # Use session state to allow no initial selection
        if key_name not in st.session_state:
            st.session_state[key_name] = None  # start unselected

        selected = st.radio(
            question,
            options,
            index=index if not allow_none else None,  # None prevents auto-selection
            key=key_name,
            help=help_text
        )
        answers[key_name] = selected

    elif input_type == "checkbox":
        st.write(question)
        if help_text:
            st.caption(help_text)

        selected = []
        cols_list = st.columns(len(options)) if columns else [st]
        for col, option in zip(cols_list, options):
            if col.checkbox(option, key=f"{key_name}_{option}"):
                selected.append(option)
        answers[key_name] = selected

    return answers[key_name]

import streamlit as st

def ask_question(
    answers,
    key_name,
    question,
    input_type="text",
    index=0,
    use_index=False,
    options=None,
    columns=True,
    help_text=None,
    allow_none=False,
    multiple=False,
    min_value=0,
    step=0
):
    """
    Generic helper to ask a question in Streamlit and store in `answers` dict.
    Parameters:
        answers (dict): dictionary to store results
        key_name (str): key to store the answer
        question (str): question text
        input_type (str): "text", "number", "radio", "checkbox", "date"
        options (list): list of options (for radio/checkbox)
        columns (bool): if radio/checkbox, display horizontally
        help_text (str): optional help text
        allow_none (bool): allow None selection for radio
        multiple (bool): allow multiple entries for text/number (line-separated)
    """
    
    if input_type in ["text", "text_input"]:
        if multiple:
            # Use a text area for multiple entries (one per line)
            values = st.text_area(f"{question} (one per line)", key=key_name, help=help_text)
            answers[key_name] = [v.strip() for v in values.split("\n") if v.strip()]
        else:
            answers[key_name] = st.text_input(question, key=key_name, help=help_text)

    elif input_type == "number":
        if multiple:
            # Text area for multiple numbers (one per line)
            values = st.text_area(f"{question} (one per line)", key=key_name, help=help_text)
            cleaned = []
            for v in values.split("\n"):
                v = v.strip()
                if v:
                    try:
                        cleaned.append(float(v))
                    except ValueError:
                        st.warning(f"Invalid number skipped: {v}")
            answers[key_name] = cleaned
        else:
            answers[key_name] = st.number_input(question, key=key_name, min_value=min_value, step=step, help=help_text)

    elif input_type == "radio":
        # Ensure session state exists
        if key_name not in st.session_state:
            st.session_state[key_name] = None  # start unselected

        radio_options = options
        if allow_none:
            radio_options = ["None"] + (options or [])

        if use_index:
            if key_name not in st.session_state or st.session_state[key_name] not in radio_options:
                if allow_none:
                    st.session_state[key_name] = "None"
                else:
                    st.session_state[key_name] = radio_options[index] if radio_options else None
            selected = st.radio(
            question,
            options=radio_options,
            key=key_name,
            help=help_text,
            horizontal=columns)
        else:
            selected = st.radio(
                question,
                options=radio_options,
                index=index if not allow_none else 0,  # start unselected if allow_none
                key=key_name,
                help=help_text,
                horizontal=columns)

        answers[key_name] = None if selected == "None" else selected

    elif input_type == "checkbox":
        st.write(question)
        if help_text:
            st.caption(help_text)

        selected = []

        if columns:
            cols_list = st.columns(len(options))
        else:
            cols_list = [st] * len(options)  # ✅ repeat st for each option

        for col, option in zip(cols_list, options):
            if col.checkbox(option, key=f"{key_name}_{option}"):
                selected.append(option)

        answers[key_name] = selected

    elif input_type == "date":
        answers[key_name] = st.date_input(question, key=key_name, help=help_text)

    return answers[key_name]





def clean_value(value):
    if value is None or value == [] or value=='':
        return "Not Answered"
    return value
































