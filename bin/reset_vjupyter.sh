#!/bin/bash -x
cd ..
poetry env remove $(poetry env list | awk '{print $1}')
oldPid=$(ps -ax | grep jupyter-notebook | grep -v grep | awk '{print $1}')
if [[ "$oldPid" != "" ]]; then
  kill -KILL $oldPid
fi
rm -f pyproject.toml poetry.lock jupyter.log
