import streamlit as st
import google.generativeai as model
import dotenv
import os
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
from io import BytesIO
from fpdf import FPDF
import pandas as pd
import logging
from datetime import datetime

dotenv.load_dotenv()
api_key = os.getenv("api_key")
model.configure(api_key=api_key)
gen1 = model.GenerativeModel(model_name="gemini-pro")
logging.basicConfig(filename='techiehelp_chatbot.log', level=logging.INFO)

def log_interaction(query, response):
    logging.info(f"Time: {datetime.now()}, User Query: {query}, AI Response: {response}")

def techiehelp_responses(user_query):
    query = user_query.lower()
    
    # Detailed information about TechieHelp
    if "about techiehelp" in query or "techiehelp" in query:
        return (
            "TechieHelp is a dynamic platform designed to empower students and professionals by providing a range of services and opportunities. Here's what we offer:\n\n"
            "- **Web Development**: We create custom websites that are responsive, user-friendly, and tailored to your business needs. Learn more about our [Web Development Services](https://techiehelp.com/web-development).\n"
            "- **App Development**: Our team develops high-quality mobile applications for both iOS and Android platforms. Explore our [App Development Services](https://techiehelp.com/app-development).\n"
            "- **SEO Services**: Improve your website's visibility and ranking on search engines with our expert SEO services. Discover more about our [SEO Services](https://techiehelp.com/seo).\n"
            "- **UI/UX Design**: We offer design services to enhance user experience and create visually appealing interfaces. Check out our [UI/UX Design Services](https://techiehelp.com/ui-ux-design).\n"
            "- **Admissions Support**: Get assistance with admissions for various educational programs and courses. Find out more about our [Admissions Support](https://techiehelp.com/admissions).\n\n"
            "TechieHelp was founded by Amit Kumar, a passionate front-end developer and AI enthusiast. Amit Kumar is committed to bridging the gap between academic learning and real-world experience. Connect with Amit on [LinkedIn](https://linkedin.com/in/amit-kumar).\n\n"
            "For more information, visit our [website](https://techiehelp.com).\n\n"
            "Connect with us on social media:\n"
            "- [Twitter](https://twitter.com/techiehelp)\n"
            "- [LinkedIn](https://linkedin.com/company/techiehelp)\n"
            "- [Facebook](https://facebook.com/techiehelp)"
        )
    
    elif "services" in query:
        return (
            "TechieHelp offers the following services:\n\n"
            "- **Web Development**: Custom websites designed to meet your needs.\n"
            "- **App Development**: Mobile apps for iOS and Android.\n"
            "- **SEO Services**: Optimize your site for better search engine rankings.\n"
            "- **UI/UX Design**: Enhance user experience with our design services.\n"
            "- **Admissions Support**: Assistance with educational program admissions.\n\n"
            "For more details, visit our [Services Page](https://techiehelp.com/services)."
        )
    elif "internships" in query:
        return (
            "TechieHelp provides internships across various domains. Our internships include:\n\n"
            "- **AI and Machine Learning**: Work on cutting-edge AI projects and gain practical experience.\n"
            "- **Web Development**: Hands-on experience with real-world web development tasks.\n"
            "- **App Development**: Develop mobile applications and gain industry insights.\n"
            "- **SEO and Digital Marketing**: Learn SEO and digital marketing strategies.\n\n"
            "Explore our [Internships Page](https://techiehelp.com/internships) for more details."
        )
    elif "mission" in query:
        return (
            "TechieHelp's mission is to bridge the gap between education and industry by providing meaningful internship and development opportunities. We aim to empower students and professionals to achieve their career goals through practical experience and expert guidance."
        )
    elif "founder" in query:
        return (
            "TechieHelp was founded by Amit Kumar, a front-end developer and AI enthusiast. Amit Kumar is dedicated to creating a platform that facilitates skill development and career advancement. Connect with Amit Kumar on [LinkedIn](https://linkedin.com/in/amit-kumar)."
        )
    elif "contact" in query:
        return "You can contact TechieHelp via email at info@techiehelp.com or visit our [website](https://techiehelp.com) for more information."
    else:
        # Use the generative model for other queries
        response = gen1.generate_content(("you are a friendly model", user_query)).text
        return response



# PDF Extraction
def extract_text_from_pdf(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text()
    return text

# Image Extraction
def extract_text_from_image(image_file):
    img = Image.open(image_file)
    text = pytesseract.image_to_string(img)
    return text

# PDF Generation
def generate_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text)
    
    pdf_buffer = BytesIO()
    pdf_buffer.write(pdf.output(dest='S').encode('latin1'))
    pdf_buffer.seek(0)
    
    return pdf_buffer

# Excel Generation
def generate_excel(query, response):
    data = {
        'User Query': [query],
        'AI Response': [response]
    }
    df = pd.DataFrame(data)
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    excel_buffer.seek(0)
    return excel_buffer

st.title("TechieHelp - AI Chatbot Assistant")
st.image("logo.png", width=150)

# Text Input for Queries
val = st.text_input(label="Ask TechieHelp Anything", placeholder="Type your question here...")

# File Uploader for PDF or Image
uploaded_file = st.file_uploader("Upload a PDF or an Image (jpg, png)", type=["pdf", "jpg", "png"])

bt = st.button("Ask TechieHelp")

if bt:
    if uploaded_file is not None:
        if uploaded_file.type == "application/pdf":
            extracted_text = extract_text_from_pdf(uploaded_file)
        elif uploaded_file.type in ["image/jpeg", "image/png"]:
            extracted_text = extract_text_from_image(uploaded_file)
        else:
            extracted_text = None

        if extracted_text:
            st.write(f"Extracted Text from File:\n{extracted_text}")
            response = techiehelp_responses(extracted_text)
            st.write(f"**TechieHelp AI:** {response}")
            log_interaction(extracted_text, response)
        else:
            st.warning("Could not extract text from the uploaded file.")
    elif val:
        response = techiehelp_responses(val)
        st.write(f"**TechieHelp AI:** {response}")
        log_interaction(val, response)

    st.sidebar.title("Download Options")

    # Generate and allow downloads
    if val or extracted_text:
        query_text = val if val else extracted_text
        response_text = techiehelp_responses(query_text)
        
        # Download as PDF
        pdf_buffer = generate_pdf(f"User Query: {query_text}\n\nAI Response: {response_text}")
        st.sidebar.download_button(
            label="Download as PDF",
            data=pdf_buffer,
            file_name="techiehelp_response.pdf",
            mime="application/pdf"
        )

        # Download as Excel
        excel_buffer = generate_excel(query_text, response_text)
        st.sidebar.download_button(
            label="Download as Excel",
            data=excel_buffer,
            file_name="techiehelp_response.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # Share on Twitter
        tweet_text = f"Check out TechieHelp's AI Chatbot! It answered: '{response_text}'"
        tweet_url = f"https://twitter.com/intent/tweet?text={tweet_text}"
        st.markdown(f"[Share on Twitter]({tweet_url})", unsafe_allow_html=True)

    else:
        st.warning("Please enter a question or upload a file before submitting.")
 