#!/bin/bash

echo "Before:"
for i in $(ls -d */); do
  du -sh $i
done
echo "$(du -sh .) Total" 

pushd lg-agent-k8s > /dev/null
  rm -rf __pycache__ logs .ipynb_checkpoints > /dev/null

  pushd conjur-setup > /dev/null
    rm -rf .info __pycache__ > /dev/null
  popd > /dev/null

  pushd conjur-test > /dev/null
    rm -rf __pycache__ logs  > /dev/null
  popd > /dev/null
popd > /dev/null

pushd lg-agent-docker > /dev/null
  rm -rf __pycache__ logs .ipynb_checkpoints > /dev/null

  pushd conjur-setup > /dev/null
    rm -rf .trust jwt-this jwt.info __pycache__  > /dev/null
  popd > /dev/null

  pushd conjur-test > /dev/null
    rm -rf __pycache__ logs  > /dev/null
  popd > /dev/null
popd > /dev/null

pushd autogen > /dev/null
  rm -rf __pycache__ logs .ipynb_checkpoints > /dev/null

  pushd conjur-setup > /dev/null
    rm -rf .trust jwt-this jwt.info __pycache__  > /dev/null
  popd > /dev/null
popd > /dev/null

pushd k8s-bot/k8s_bot > /dev/null
  rm -rf __pycache__ > /dev/null
  pushd agents > /dev/null
    rm -rf __pycache__ > /dev/null
  popd > /dev/null
popd > /dev/null

echo
echo
echo "After:"
for i in $(ls -d */); do
  du -sh $i
done
echo "$(du -sh .) Total" 

