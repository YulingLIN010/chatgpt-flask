from flask import Flask, request, jsonify
from flask_cors import CORS
import openai, os, base64

app = Flask(__name__)
CORS(app)
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 讀取你的風格知識庫
with open('styles.txt', encoding='utf-8') as f:
    styles_text = f.read()

prompt_base = f"""
你是一位專業室內設計師，請根據使用者上傳的照片，從"styles.txt"已定義的風格中找出最貼近者（北歐風、工業風、混搭風、簡約風、鄉村風、現代風、古典風、新古典風、日式侘寂風、日式禪風、日式無印風、地中海風、美式風）。
{styles_text}

分析步驟如下：
1【風格判斷】：照片屬於哪一種風格？  
2【判斷依據】：請列出推論依據（至少3點）  
3【設計理念】：列出該風格的5個核心理念（由先備知識撈取）
4【建材分析】：列出空間所使用的建材，並解釋其與風格的關聯    
5【色彩規劃】：列出該風格的色彩規劃（由先備知識撈取）  
6【空間命名】：根據圖片的設計內容給予一個富有故事性的名稱，並描述命名的故事內容及由來。  
7【社群文案】：撰寫250字的社群文案，語氣具備"設計師專業"及"文青溫馨" 2種版本的文案供使用者選擇，也加入2~5個Emoji與Hashtag

請以繁體中文完整回覆，並內容可直接用於平台發布。
"""

@app.route("/api/design_copy", methods=["POST"])
def design_copy():
    if 'image' not in request.files:
        return jsonify({"reply": "未收到圖片，請重新上傳！"}), 400
    img_file = request.files['image']
    img_bytes = img_file.read()
    img_b64 = base64.b64encode(img_bytes).decode("utf-8")

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": prompt_base},
            {
                "role": "user",
                "content": [
                    # ⚠️ 必須用 dict 格式
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}},
                    {"type": "text", "text": prompt_base}
                ]
            }
        ]
    )
    reply = response.choices[0].message.content
    return jsonify({"reply": reply})

@app.route("/")
def index():
    return "室內設計風格辨識小幫手 API 運作中..請稍等"

