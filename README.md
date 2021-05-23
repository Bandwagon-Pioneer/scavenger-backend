# scavenger-backend

### authenticate w/ ngrok
ngrok authtoken [AUTHTOKEN]

### open tunnels to your machine
ngrok http -region=us -hostname=bandwagon.ngrok.io 5000

ngrok http -region=us -hostname=holloway-hunt.ngrok.io 80

### startup servers

cd FRONTEND/BUILD
pm2 serve build 80 --spa

cd BACKEND
EITHER:
- gunicorn --bind 0.0.0.0:5000 wsgi:app
- python3 -m gunicorn --bind 0.0.0.0:5000 wsgi:app

### good to go!
