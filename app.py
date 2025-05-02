from flask import Flask, render_template,request
import os
from PyPDF2 import PdfReader
import spacy

#initialize Flask app
app=Flask(__name__)

#Load spacy NLP model
nlp=spacy.load("en_core_web_sm")

#func to extract text from pdf file
def extract_text_from_pdf(pdf_file):
    reader= PdfReader(pdf_file)
    text=""
    for page in reader.pages:
        text+=page.extract_text()
    return text

#Func to perform basic nlp analysis on the extracted resume text
def analyze_resume(resume_text):
    doc=nlp(resume_text)
    
#Extract entities like skills,companies, and educations
    skills=[ent.text for ent in doc.ents if ent.label_=="SKILL" or ent.label_=="ORG"]
    education=[sent.text for sent in doc.sents if 'degree' in sent.text.lower() or 'university' in sent.text.lower()]
    experience=[sent.text for sent in doc.sents if 'experience' in sent.text.lower() or 'worked' in sent.text.lower()]
    return skills, education, experience

#route for home page(uploading resume and displaying analysis)
@app.route("/", methods=["GET", "POST"])
def upload_resume():
    if request.method=="POST":
        if 'resume' not in request.files:
            return "No file part"
        file=request.files['resume']
        if file.filename=="":
            return "No selected file"
        if file:
            file_path=os.path.join("uploads", file.filename)
            file.save(file_path)
            resume_text=extract_text_from_pdf(file_path)
            skills, education, experience=analyze_resume(resume_text)
            return render_template("index.html", skills=skills, education=education, experience=experience)
    return render_template("index.html",skills=None, education=None, experience=None)

if __name__=="__main__":
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    app.run(debug=True)