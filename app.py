from flask import Flask, Request, Response, jsonify, render_template, request, send_file
import requests
import pandas as pd
from pdfquery import PDFQuery
import openai
from youtube_transcript_api import YouTubeTranscriptApi 
from fpdf import FPDF
from datetime import datetime

app = Flask(__name__)

openai.api_base = "https://api.pawan.krd/v1"
openai.api_key = "pk-OdxKVZfMTWFSMLfWNQAjKcvciNrfupCUodTcPyxCMdlqUAQA"

history = []

@app.route("/api/messages", methods=["POST"])
def chat_bot():
    message = request.json
    message = message.get("message")
    start_time = datetime.now()
    if(message == "END"):
        history.clear()
        return jsonify({"response": "ENDED CONVERSATION"})
    else:
        history.append({"role":"user","content":message})
        chat_completion = openai.ChatCompletion.create(
            model="pai-001-light-beta",
            messages=history
        )
        response = chat_completion.choices[0].message.content
        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds()
        print(f"Response Time: {response_time} seconds")
        history.append({"role":"assistant","content": response})
        conversation = [(history[i]["content"],history[i+1]["content"]) for i in range(0, len(history)-1, 2)]
        return jsonify({"response": response})

def model(message):
    start_time = datetime.now()
    if(message == "END"):
        history.clear()
        return "ENDED CONVERSATION"
    else:
        history.append({"role":"user","content":message})
        chat_completion = openai.ChatCompletion.create(
            model="pai-001-light-beta",
            messages=history
        )
        response = chat_completion.choices[0].message.content
        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds()
        print(f"Response Time: {response_time} seconds")
        history.append({"role":"assistant","content": response})
        conversation = [(history[i]["content"],history[i+1]["content"]) for i in range(0, len(history)-1, 2)]
        return response
    
@app.route('/api/material', methods=['POST'])
def receive_material():
    global text_content
    try:
        contentType = request.form.get('type')
        if(contentType == "PDF"):
            file = request.files.get('content')
            pdf = PDFQuery(file)
            pdf.load()
            text_elements = pdf.pq('LTTextLineHorizontal')
            text_content = " ".join(t.text.strip() for t in text_elements if t.text.strip())

        elif(contentType=="TXT"):
            file = request.files.get('content')
            text_content = file.read().decode('utf-8')
            text_content = "\n".join(line.strip() for line in text_content.splitlines() if line.strip())
        
        elif(contentType=="YT"):
            youtube = request.form.get('content')
            transcript = YouTubeTranscriptApi.get_transcript(youtube)
            text_content = [entry['text'] for entry in transcript]
            text_content = ' '.join(text_content)

        elif(contentType=="PT"):
            text_content = request.form.get('content')
        else:
            text_content = ""

        return jsonify({'message': 'Material uploaded successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/generate_material', methods=['POST'])
def generate_material():
    model("END")
    message = request.form.get('type')
    if(message == "Quiz"):
        prompt = "Test me on the passage below and ask at least 5 questions. \n" + text_content
        response =  model(prompt)

        return jsonify({'message': response}), 200
    elif(message == "Teach"):
        prompt = "Teach me the passage below. \n" + text_content
        response =  model(prompt)

        return jsonify({'message': response}), 200
    elif(message == "NotesPDF"):
        prompt = "Please generate a 1-4 page notes packet based off the text below. Format it nicely.\n" + text_content
        response =  model(prompt)

        response = response.replace('?', '?\n')

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, response)

        pdf_path = 'PalBotQuiz.pdf'
        pdf.output(pdf_path)

        return send_file(pdf_path, as_attachment=True)
    elif(message == "QuizPDF"):
        prompt = "Please generate a 15 question with problems based off the text below. Format it nicely. \n" + text_content
        response =  model(prompt)
        response = response.replace('?', '?\n')

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, response)

        pdf_path = 'PalBotQuiz.pdf'
        pdf.output(pdf_path)

        return send_file(pdf_path, as_attachment=True)


@app.route('/api/quiz_window', methods=['POST'])
def quiz_window():
    model("END")
    sentence = request.form.get('sentence')
    response = model(sentence)
    response = response.replace('?', '?\n')
    return jsonify({'message': response}), 200

@app.route('/api/download_pdf', methods=['POST'])
def download_pdf():
    model("END")
    sentence = request.form.get('sentence')
    response = model(sentence)
    response = response.replace('?', '?\n')

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, response)

    pdf_path = 'PalBotQuiz.pdf'
    pdf.output(pdf_path)
    return send_file(pdf_path, as_attachment=True)

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(host="localhost", port=8000, debug=True)