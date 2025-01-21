#!/bin/bash

declare -a FILES_TO_DELETE=(
".trust"
"jwt-this"
"jwt.info"
"*.log"
)

declare -a DIRS_TO_DELETE=(
".info"
".ipynb_checkpoints"
"__pycache__"
".cache"
)

echo "Before:"
for i in $(ls -d */); do
  du -sh $i
done
echo "$(du -sh .) Total" 

# kill jupyter env
pushd bin
  ./reset_vjupyter.sh
popd

# kill running jwt-this
PID=$(ps -ax | grep "http://jwt-this" | grep -v grep | awk '{print $2}')
kill -9 $PID

for i in "${FILES_TO_DELETE[@]}"; do
  rm_me=$(find . -type f -name "$i" -print)
  for f in $rm_me; do
    rm $f
  done
done

for i in "${DIRS_TO_DELETE[@]}"; do
  rm_me=$(find . -type d -name "$i" -print)
  for d in $rm_me; do
    rm -rf $d
  done
done

echo
echo
echo "After:"
for i in $(ls -d */); do
  du -sh $i
done
echo "$(du -sh .) Total" 

