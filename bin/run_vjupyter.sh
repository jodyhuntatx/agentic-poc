#!/bin/bash
source set_api_keys.sh
cd ..
poetry init --name=${PWD##*/} --description="jupyter notebook runtime" --author="jodyhuntatx"
poetry add jupyter
#oldPid=$(ps -ax | grep jupyter | grep -v grep | awk '{print $1}')
oldPid=""
if [[ "$oldPid" != "" ]]; then
  kill -9 $oldPid
fi
poetry run jupyter notebook 2> jupyter.log &
