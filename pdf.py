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


def section_header(pdf, title):
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 10, title, ln=True)
    pdf.ln(2)

def section_break(pdf, new_page=False):
    if new_page:
        pdf.add_page()
    else:
        pdf.ln(6)


