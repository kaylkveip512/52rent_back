## Development tools

This project uses external development tools that are not installed via pip.

### MailHog
MailHog is used for catching outgoing emails in development.

Installation:
- Windows: https://github.com/mailhog/MailHog/releases
- macOS: brew install mailhog
- Linux: sudo apt install mailhog

Run:
mailhog

Web UI:
http://127.0.0.1:8025

### ngrok
ngrok is used to expose localhost for payment callbacks (LiqPay).

Installation:
https://ngrok.com/download

After installation:
ngrok config add-authtoken <YOUR_TOKEN>

Run:
ngrok http 8000

for seeing requests:
http://127.0.0.1:4040
