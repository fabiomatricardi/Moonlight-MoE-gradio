import gradio as gr
from openai import OpenAI
import random
import string
import datetime

# One API key to rule them all
# - create a logfile for the chat
# - LOG the changes in Model and truncation of the Chat messages in case of MAX LENGHT reached

def writehistory(filename,text):
    """
    save a string into a logfile with python file operations
    filename -> str pathfile/filename
    text -> str, the text to be written in the file
    """
    with open(f'{filename}', 'a', encoding='utf-8') as f:
        f.write(text)
        f.write('\n')
    f.close()

def genRANstring(n):
    """
    n = int number of char to randomize
    Return -> str, the filename with n random alphanumeric charachters
    """
    N = n
    res = ''.join(random.choices(string.ascii_uppercase +
                                string.digits, k=N))
    print(f'Logfile_{res}.md  CREATED')
    return f'Logfile_{res}.md'

logafilename = genRANstring(5)
note = """#### ⚠️ Remember to put your API key for Open Router
> you can find the field in the Additional Inputs<br>
> you can get an API key for free from [openrouter.ai](https://openrouter.ai/settings/keys)
<br>Starting settings: `Temperature=0.45` `Max_Length=2048`
"""
note2 = """#### 🌔 MoonShot AI
> [Moonlight 16B A3B Instruct](https://huggingface.co/moonshotai) is a 16B-parameter Mixture-of-Experts (MoE) language model developed by Moonshot AI. It is optimized for instruction-following tasks with 3B activated parameters per inference. The model advances the Pareto frontier in performance per FLOP across English, coding, math, and Chinese benchmarks.<br>
> It outperforms comparable models like Llama3-3B and Deepseek-v2-Lite while maintaining efficient deployment capabilities through Hugging Face integration and compatibility with popular inference engines like vLLM12.
 [moonshot.ai](https://www.moonshot.cn/)
"""

mycss = """
#warning {justify-content: center; text-align: center}
"""

with gr.Blocks(theme=gr.themes.Citrus(),fill_width=True,css=mycss) as demo: #gr.themes.Ocean() #https://www.gradio.app/guides/theming-guide
        gr.Markdown("# Chat with Moonlight-16b-a3b 🌔 a MoE to use worldwide",elem_id='warning')
        with gr.Row():
            with gr.Column(scale=1):
                maxlen = gr.Slider(minimum=250, maximum=4096, value=2048, step=1, label="Max new tokens")
                temperature = gr.Slider(minimum=0.1, maximum=4.0, value=0.45, step=0.1, label="Temperature")          
                APIKey = gr.Textbox(value="", 
                            label="Open Router API key",
                            type='password',placeholder='Paste your API key',)
                gr.Markdown(note)
                log = gr.Markdown(logafilename, label='Log File name')
                gr.Markdown(note2)
            with gr.Column(scale=3):
                chatbot = gr.Chatbot(type="messages",min_height='65vh',show_copy_button = True,
                    avatar_images=['https://i.ibb.co/PvqbDphL/user.png',
                                   'https://i.ibb.co/vxvCwBTX/moonlight.png'],)
                msg = gr.Textbox(placeholder='Shift+Enter to add a new line...')
                clear = gr.ClearButton([msg, chatbot])

                def user(user_message, history: list):
                    logging = f'USER> {user_message}\n'
                    writehistory(logafilename,logging)
                    return "", history + [{"role": "user", "content": user_message}]
                        

                def respond(chat_history, api,t,m):
                    client = OpenAI(
                            base_url="https://openrouter.ai/api/v1",
                            api_key=api,
                            )
                    stream = client.chat.completions.create(
                        extra_headers={
                            "HTTP-Referer": "https://thepoorgpuguy.substack.com/", # Optional. Site URL for rankings on openrouter.ai.
                            "X-Title": "Fabio Matricardi is The Poor GPU Guy", # Optional. Site title for rankings on openrouter.ai.
                        },
                        extra_body={},
                        model="moonshotai/moonlight-16b-a3b-instruct:free", #rekaai/reka-flash-3:free       
                        messages=chat_history,
                        max_tokens=m,
                        stream=True,
                        temperature=t)
                    chat_history.append({"role": "assistant", "content": ""})
                    for chunk in stream:
                        chat_history[-1]['content'] += chunk.choices[0].delta.content

                        yield chat_history
                    logging = f"USER> {chat_history[-1]['content']}\n"
                    writehistory(logafilename,logging)                   


        msg.submit(user, [msg, chatbot], [msg, chatbot]).then(
            respond, [chatbot,APIKey,temperature,maxlen], [chatbot])


# RUN THE MAIN
if __name__ == "__main__":
    demo.launch(inbrowser=True)