import openai
import gradio

openai.api_base = "https://api.pawan.krd/v1"
openai.api_key = "pk-OdxKVZfMTWFSMLfWNQAjKcvciNrfupCUodTcPyxCMdlqUAQA"

history = [{"role": "system", "content": "You are a helpful teacher."}]

def chat_bot(message):
    history.append({"role":"user","content":message})
    chat_completion = openai.ChatCompletion.create(
        model="pai-001-light-beta",
        messages=history
    )
    response = chat_completion.choices[0].message.content
    history.append({"role":"assistant","content": response})

    conversation = [(history[i]["content"],history[i+1]["content"]) for i in range(0, len(history)-1, 2)]
    print(conversation)
    return "", conversation
with gradio.Blocks() as chatbot_ui:
    history = []
    gradio.Markdown("""<h1><center>Parth's Chatbot</center></h1>""")
    chatbot = gradio.Chatbot()
    txt = gradio.Textbox(show_label=False, placeholder="Chat with Parth's AI Chatbot")
    submit = gradio.Button("Send")
    submit.click(chat_bot, inputs=txt, outputs=[txt,chatbot])

chatbot_ui.launch()