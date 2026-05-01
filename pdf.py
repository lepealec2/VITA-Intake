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


def generate_pdf(answers_dict):
    import datetime
    from fpdf import FPDF
    class MyPDF(FPDF):
        def footer(self):
            self.set_y(-15)
            self.set_font("Arial", "I", 8)
            self.cell(0, 10, f"Page {self.page_no()} of {{nb}}", align="C")
    pdf = MyPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.alias_nb_pages()

    # 🚨 DO NOT add a title page or header
    pdf.add_page()

    # start directly with real content
    # example:
    pdf.set_font("Arial", "", 11)

    def clean(v):
        if v is None:
            return "Not answered"
        if isinstance(v, str) and not v.strip():
            return "Not answered"
        if isinstance(v, (list, dict)) and not v:
            return "Not answered"
        s = str(v)
        return s
    name = answers_dict.get("name", "questionnaire").replace(" ", "_")
    filename = f"{name}.pdf"
    filename = ".pdf"
    pdf.set_auto_page_break(auto=True, margin=15)
#    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Supplemental Questionnaire", ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("Arial", "", 11)

    for key, value in answers_dict.items():
        if key.lower() in ("cdcc_children" "edu_students" "ssa"):
            continue
        if key=="PII":
            pdf.set_font("Arial", "B", 11)
            pdf.cell(0, 7, f"Basic Information", ln=True)
            pdf.set_font("Arial", "", 11)
        if key=="Health_Insurance":
            pdf.set_font("Arial", "B", 11)
            pdf.cell(0, 7, f"Health Insurance", ln=True)
            pdf.set_font("Arial", "", 11)
        if isinstance(value, list):
            pdf.set_font("Arial", "", 11)
            pdf.cell(0, 6, f"{key.replace('_',' ').title()}:", ln=True)
            for item in value:
                pdf.multi_cell(0, 6, f"[X] {item}")
            pdf.ln(2)
            continue
        if key=="Renter_Status":
            pdf.set_font("Arial", "B", 11)
            pdf.cell(0, 7, f"Renter Status", ln=True)
            pdf.set_font("Arial", "", 11)
        if key=="IHSS":
            pdf.set_font("Arial", "B", 11)
            pdf.cell(0, 7, f"Miscellanous Questions", ln=True)
            pdf.set_font("Arial", "", 11)
        if key=="W-2s":
            pdf.set_font("Arial", "B", 11)
            pdf.cell(0, 7, f"Income", ln=True)
            pdf.set_font("Arial", "", 11)
        if key=="Student_Loan_Interest":
            pdf.set_font("Arial", "B", 11)
            pdf.cell(0, 7, f"Deductions and Credits", ln=True)
            pdf.set_font("Arial", "", 11)
        
        # =========================
        # ESTIMATED TAX
        # =========================
        tax_year = answers_dict.get("taxyear", "2025")

        if key.lower() == "estimatedtax" and isinstance(value, dict):
            pdf.set_font("Arial", "B", 11)
            pdf.cell(0, 8, "Estimated Tax Payments", ln=True)
            pdf.set_font("Arial", "", 11)

            col_width = pdf.w / 2 - 15
            quarters = ["Q1", "Q2", "Q3", "Q4"]

            def get_vals(q):
                return (
                    value.get(f"{q}_{tax_year}_FD", 0),
                    value.get(f"{q}_{tax_year}_CA", 0)
                )

            for i in range(0, 4, 2):
                q1, q2 = quarters[i], quarters[i + 1]

                x = pdf.get_x()
                y = pdf.get_y()

                fd1, ca1 = get_vals(q1)
                fd2, ca2 = get_vals(q2)

                pdf.multi_cell(col_width, 6,
                    f"{q1} {tax_year}\nFederal: {fd1}\nCA: {ca1}",
                    border=1
                )

                pdf.set_xy(x + col_width, y)

                pdf.multi_cell(col_width, 6,
                    f"{q2} {tax_year}\nFederal: {fd2}\nCA: {ca2}",
                    border=1
                )
                pdf.ln(2)
            continue
        # =========================
        # SCHEDULE C DETAILS
        # =========================

        if key == "Schedule_C_Details":

            schc = value  # this is the full dict
            businesses = schc.get("businesses", [])

            expense_order = [
                "advertising",
                "contract_labor",
                "commission_and_fees",
                "depletion",
                "employee_benefit_programs",
                "health_insurance",
                "insurance_other_than_health"
                "long_term_care",
                "mortgage_interest",
                "other_interest",
                "office_expenses"
                "pension_and_profit_sharing",
                "legal_and_professional_services",
                "rent_or_lease_of_equipment",
                "rent_or_lease_of_property",
                "repairs_and_maintenance",
                "supplies",
                "taxes_and_licenses",
                "travel",
                "meals_50_per",
                "meals_80_per",
                "utilities",
                "wages",
                "other_expenses"
            ]
            expense_order = [
                "advertising",   "pension_and_profit_sharing",
                "contract_labor","rent_or_lease_of_equipment",
                "commission_and_fees",  "rent_or_lease_of_property",
                "depletion", "repairs_and_maintenance",
                "employee_benefit_programs", "supplies",
                "health_insurance", "taxes_and_licenses",
                "insurance_other_than_health", "travel",
                "long_term_care","meals_50_per",
                "mortgage_interest", "meals_80_per",
                "other_interest",  "utilities",
                "legal_and_professional_services","wages",
                "office_expenses",  "other_expenses"
            ]            
            def labelize(k):
                return k.replace("_", " ").title()

            col_w = (pdf.w - pdf.l_margin - pdf.r_margin) / 4
            row_h = 7

            for i, biz in enumerate(businesses):

#                pdf.add_page()
                pdf.set_font("Arial", "B", 11)
                pdf.cell(0, 7, f"Business #{i+1}", ln=True)
                pdf.ln(1)

                # =========================
                # INCOME
                # =========================
                pdf.set_font("Arial", "B", 11)
                pdf.cell(0, 6, "Income", ln=True)
                pdf.set_font("Arial", "", 11)

                income_fields = [
                    "1099_nec_amounts",
                    "1099_k_amounts",
                    "1099_misc_amounts",
                    "other_cash_income",
                    "business_type",
                    "other_business"
                ]

                for k in income_fields:
                    if k in biz:
                        pdf.cell(70, 6, f"{labelize(k)}:", border=0)
                        pdf.cell(0, 6, clean(biz.get(k)), ln=True)

                pdf.ln(2)

                # =========================
                # EXPENSE TABLE
                # =========================
                pdf.set_font("Arial", "B", 9)

                headers = ["Expense", "Amount", "Expense", "Amount"]
                for h in headers:
                    pdf.cell(col_w, row_h, h, border=1, align="C")
                pdf.ln()

                pdf.set_font("Arial", "", 9)

                ordered = [(k, clean(biz.get(k, 0))) for k in expense_order if k in biz]

                odd, even = [], []

                for k, v in ordered:
                    if (expense_order.index(k) + 1) % 2:
                        odd.append((k, v))
                    else:
                        even.append((k, v))

                max_len = max(len(odd), len(even))

                for idx in range(max_len):
                    l = odd[idx] if idx < len(odd) else ("", "")
                    r = even[idx] if idx < len(even) else ("", "")

                    pdf.cell(col_w, row_h, labelize(l[0]) if l[0] else "", border=1)
                    pdf.cell(col_w, row_h, str(l[1]) if l[1] else "", border=1)

                    pdf.cell(col_w, row_h, labelize(r[0]) if r[0] else "", border=1)
                    pdf.cell(col_w, row_h, str(r[1]) if r[1] else "", border=1)

                    pdf.ln(row_h)

                pdf.ln(4)

                # =========================
                # VEHICLE
                # =========================
                pdf.set_font("Arial", "B", 10)
                pdf.cell(0, 6, "Vehicle Information", ln=True)
                pdf.set_font("Arial", "", 9)

                vehicle_map = {
                    "vehicle_desc": "SCH_C_vehicle_desc",
                    "vehicle_date": "SCH_C_vehicle_date",
                    "business_miles": "business_miles",
                    "vehicle_other": "SCH_C_vehicle_other",
                    "vehicle_off_duty": "SCH_C_vehicle_off_duty",
                    "vehicle_evidence": "SCH_C_vehicle_evidence"
                }

                for k, pdf_label in vehicle_map.items():
                    if k in biz:
                        pdf.cell(70, 6, f"{labelize(pdf_label)}:", border=0)
                        pdf.cell(0, 6, clean(biz.get(k)), ln=True)

                pdf.ln(2)
        if key == "SSA_Lump_Sum_Detail":

            data = value or {}
            years = data.get("lump_sum_details") or []

            if not years:
                continue

            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 8, "Social Security Lump-Sum Details", ln=True)
            pdf.ln(2)

            def val(x):
                return "" if x is None else str(x)

            for i, year in enumerate(years, start=1):

                if not isinstance(year, dict):
                    continue

                pdf.set_font("Arial", "B", 11)
                pdf.cell(0, 7, f"Prior Year #{i}", ln=True)

                pdf.set_font("Arial", "", 10)

                pdf.cell(60, 6, "Tax Year:", border=0)
                pdf.cell(0, 6, val(year.get("Tax_Year")), ln=True)

                pdf.cell(60, 6, "Filing Status:", border=0)
                pdf.cell(0, 6, val(year.get("Filing_Status")), ln=True)

                pdf.cell(60, 6, "Gross SSA:", border=0)
                pdf.cell(0, 6, val(year.get("Gross_SSA")), ln=True)

                pdf.cell(60, 6, "Lump Sum:", border=0)
                pdf.cell(0, 6, val(year.get("Lump_Sum")), ln=True)

                pdf.cell(60, 6, "Taxable SSA:", border=0)
                pdf.cell(0, 6, val(year.get("Taxable_SSA")), ln=True)

                pdf.cell(60, 6, "AGI:", border=0)
                pdf.cell(0, 6, val(year.get("AGI")), ln=True)

                pdf.cell(60, 6, "Adjustments:", border=0)
                pdf.cell(0, 6, val(year.get("Adjustments")), ln=True)

                pdf.cell(60, 6, "Tax-Exempt Interest:", border=0)
                pdf.cell(0, 6, val(year.get("Tax_Exempt_Interest")), ln=True)

                pdf.cell(60, 6, "Taxable SSA:", border=0)
                pdf.cell(0, 6, val(year.get("Taxable_SSA")), ln=True)

                pdf.cell(60, 6, "Net SSA:", border=0)
                pdf.cell(0, 6, val(year.get("Net_SSA")), ln=True)

                pdf.ln(3)

            continue
        # =========================
        # CDCC
        # =========================
        
        if key == "CDCC_Details":
            children = (value or {}).get("children") or []
            if children:
#                pdf.add_page() 
                if isinstance(children, list) and children:
                    pdf.set_font("Arial", "B", 12)
                    pdf.cell(0, 8, "Child & Dependent Care Credit", ln=True)
                    pdf.ln(2)
                    for i, child in enumerate(children, start=1):
                        if not isinstance(child, dict):
                            continue
                        pdf.set_font("Arial", "B", 11)
                        pdf.cell(0, 7, f"Child #{i}", ln=True)
                        pdf.set_font("Arial", "", 10)
                        name = child.get("Name") or "Not Answered"
                        pdf.cell(60, 6, "Name:", border=0)
                        pdf.cell(0, 6, str(child.get("Name") or 0), ln=True)
                        pdf.cell(60, 6, "Birthday:", border=0)
                        pdf.cell(0, 6, str(child.get("Birthday") or "Not Answered"), ln=True)
                        pdf.cell(60, 6, "Provider_ID_Type:", border=0)
                        pdf.cell(0, 6, str(child.get("Provider_ID_Type") or "Not Answered"), ln=True)
                        pdf.cell(60, 6, "Provider_EIN:", border=0)
                        pdf.cell(0, 6, str(child.get("Provider_EIN") or "Not Answered"), ln=True)
                        pdf.cell(60, 6, "Provider_SSN", border=0)
                        pdf.cell(0, 6, str(child.get("Provider_SSN") or "Not Answered"), ln=True)
                        pdf.cell(60, 6, "Provider_Name:", border=0)
                        pdf.cell(0, 6, str(child.get("Provider_Name") or "Not Answered"), ln=True)
                        pdf.cell(60, 6, "Provider_Address:", border=0)
                        pdf.cell(0, 6, str(child.get("Provider_Address") or "Not Answered"), ln=True)
                        pdf.cell(60, 6, "Provider_Phone_Number:", border=0)
                        pdf.cell(0, 6, str(child.get("Provider_Phone_Number") or "Not Answered"), ln=True)
                        pdf.ln(3)
#                pdf.add_page() 
                continue

        # =========================
        # EDUCATION
        # =========================
        if key == "EducationCredits":
#            print(key)
            students = (value or {}).get("students") or []
            if students:
                for i, stu in enumerate(students, 1):
                    pdf.set_font("Arial", "B", 12)
                    pdf.cell(0, 8, "Education Credits", ln=True)
                    pdf.ln(2)
                    if not isinstance(stu, dict):
                        continue
                    pdf.set_font("Arial", "B", 11)
                    pdf.cell(0, 7, f"Student #{i}", ln=True)
                    pdf.set_font("Arial", "", 10)
                    def val(x):
                        return "Not Answered" if x is None else str(x)
                    
                    pdf.cell(60, 6, "Name:", border=0)
                    pdf.cell(0, 6, val(stu.get("Name")), ln=True)

                    pdf.cell(60, 6, "Relationship:", border=0)
                    pdf.cell(0, 6, val(stu.get("Relationship")), ln=True)

                    pdf.cell(60, 6, "Age:", border=0)
                    pdf.cell(0, 6, val(stu.get("Age")), ln=True)

                    pdf.cell(60, 6, "Enrollment Status:", border=0)
                    pdf.cell(0, 6, val(stu.get("Enrollment_Status")), ln=True)

                    pdf.cell(60, 6, "Level:", border=0)
                    pdf.cell(0, 6, val(stu.get("Level")), ln=True)

                    pdf.cell(60, 6, "Years Post Secondary:", border=0)
                    pdf.cell(0, 6, val(stu.get("Years_Post_Secondary")), ln=True)

                    pdf.cell(60, 6, "Felony Drug:", border=0)
                    pdf.cell(0, 6, val(stu.get("Felony_Drug")), ln=True)

                    pdf.cell(60, 6, "AOTC:", border=0)
                    pdf.cell(0, 6, val(stu.get("AOTC")), ln=True)

                    pdf.cell(60, 6, "Box 4 or 6 (Adjustments, OOS):", border=0)
                    pdf.cell(0, 6, val(stu.get("box4_or_6")), ln=True)

                    pdf.cell(60, 6, "Payments Box 1:", border=0)
                    pdf.cell(0, 6, val(stu.get("Payments_Box1")), ln=True)

                    pdf.cell(60, 6, "Scholarships Box 5:", border=0)
                    pdf.cell(0, 6, val(stu.get("Scholarships_Box5")), ln=True)

                    pdf.cell(60, 6, "Additional Qualified Expenses:", border=0)
                    pdf.cell(0, 6, val(stu.get("Additional_Qualified_Expenses")), ln=True)

                    pdf.cell(60, 6, "Education Credit:", border=0)
                    pdf.cell(0, 6, val(stu.get("Education_Credit")), ln=True)

                    pdf.ln(3)
#            pdf.add_page()
            continue
        if key=="IRS_Refund":
            pdf.set_font("Arial", "B", 11)
            pdf.cell(0, 7, f"Refund Method and Payment", ln=True)
            pdf.set_font("Arial", "", 11)



        # 1. None first
        if value is None:
            pdf.cell(70, 6, f"{key.replace('_',' ')}:", border=0)
            pdf.cell(0, 6, "Not answered", ln=True)
            continue
        if not isinstance(value, dict):
            pdf.cell(70, 6, f"{key.replace('_',' ')}:", border=0)
            pdf.multi_cell(0, 6, clean(value))
    # =========================
    # IMPORTANT: STREAMLIT SAFE OUTPUT
    # =========================
    pdf_bytes = pdf.output(dest="S").encode("latin-1")

    return {
        "pdf_bytes": pdf_bytes,
        "filename": filename
    }