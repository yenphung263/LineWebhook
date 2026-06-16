
import os
from flask import Flask, request, abort
from dotenv import load_dotenv

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# load .env from project root
load_dotenv()

# read credentials from environment (now loaded from .env)
CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

if not CHANNEL_SECRET or not CHANNEL_ACCESS_TOKEN:
	raise RuntimeError(
		"Please set LINE_CHANNEL_SECRET and LINE_CHANNEL_ACCESS_TOKEN environment variables"
	)

app = Flask(__name__)
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)


@app.route("/callback", methods=["POST"])
def callback():
	signature = request.headers.get("X-Line-Signature", "")
	body = request.get_data(as_text=True)

	try:
		handler.handle(body, signature)
	except InvalidSignatureError:
		abort(400)

	return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event: MessageEvent):
	incoming = event.message.text
	reply = TextSendMessage(text=incoming)
	line_bot_api.reply_message(event.reply_token, reply)


if __name__ == "__main__":
	port = int(os.getenv("PORT", 5000))
	app.run(host="0.0.0.0", port=port, debug=True)

