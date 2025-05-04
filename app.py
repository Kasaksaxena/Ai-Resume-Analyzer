from flask import Flask, render_template,request
import os
from PyPDF2 import PdfReader
import spacy
import nltk
from nltk.corpus import wordnet as wn

#initialize Flask app
app=Flask(__name__)

#Load spacy NLP model
nlp=spacy.load("en_core_web_sm")
nltk.download('wordnet')
nltk.download('omw-1.4')

#func to extract text from pdf file
def extract_text_from_pdf(pdf_file):
    reader= PdfReader(pdf_file)
    text=""
    for page in reader.pages:
        text+=page.extract_text()
    return text

# Sample job description for comparison
resume_skills=["Python", "Django", "REST APIs", "SQL", "Git", "AWS", "JavaScript","VSCode","AI","CI","Bachelor of Technology","Data Science"]
job_description = """
We are hiring a Python backend developer with experience in Django, REST APIs, and SQL. 
Familiarity with Git, deployment, and cloud services like AWS or Azure is a plus. 
Good communication skills and teamwork are essential.
"""

#Func to perform basic nlp analysis on the extracted resume text
def analyze_resume(resume_text):
    doc=nlp(resume_text)
    
#Extract entities like skills,companies, and educations
    skills=[ent.text for ent in doc.ents if ent.label_=="SKILL" or ent.label_=="ORG"]
    education=[sent.text for sent in doc.sents if 'degree' in sent.text.lower() or 'university' in sent.text.lower()]
    experience=[sent.text for sent in doc.sents if 'experience' in sent.text.lower() or 'worked' in sent.text.lower()]
    return skills, education, experience

#Function to get synonyms for a word using WordNet
def get_synonyms(word):
    synonyms = set()
    for syn in wn.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name().lower())
    return synonyms

def calculate_match_score(resume_skills, job_description_text):
    job_doc = nlp(job_description_text.lower())
    job_keywords = {token.text for token in job_doc if token.is_alpha and not token.is_stop}
    
    #Add synonyms for job keywords
    all_job_keywords = set(job_keywords)
    for keyword in job_keywords:
        synonyms = get_synonyms(keyword)
        all_job_keywords.update(synonyms)

    matched_skills = [skill for skill in resume_skills if skill.lower() in all_job_keywords]
    score = (len(matched_skills) / len(resume_skills)) * 100 

    return round(score, 2), matched_skills

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
            score,matched=calculate_match_score(resume_skills, job_description)
            return render_template("index.html", skills=skills, education=education, experience=experience , score=score, matched=matched)
    return render_template("index.html",skills=None, education=None, experience=None, score=None, matched=None)

if __name__=="__main__":
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    app.run(debug=True)