#!/bin/bash
echo "Detach: 'Ctrl-b d'"
echo "Attach: 'tmux attach -t jupyter"
read -n 1 -s -r -p "Press any key to continue"
cd ~
if ! test -f .ssh/mycert.pem; then
  openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout .ssh/mykey.key -out .ssh/mycert.pem
fi
tmux new -s jupyter jupyter notebook --no-browser --port=3000 --ServerApp.ip=0.0.0.0 --certfile=.ssh/mycert.pem --keyfile .ssh/mykey.key

