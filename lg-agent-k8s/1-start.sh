#!/bin/bash 
set -o pipefail

source ./agent-vars.sh

main() {
  ./stop
  build_image
  start_container
}

build_image() {
  pushd build
    docker build -t $AGENT_IMAGE .
  popd
}

start_container() {
    kubectl apply -f lg-agent-manifest.yaml
    AGENT_POD=$(kubectl get pods -n lg-agent --no-headers | awk '{print $1}')
    kubectl wait --for=condition=Ready pod/$AGENT_POD -n lg-agent

    # Replicate keyring values into container keyring
    keynames=("openaiapi" "mistralapi" "tavilyapi" "langchainapi" "newjodybotpwd")
    for key in "${keynames[@]}" ; do
      echo $(keyring get cybrid $key) 	\
	| kubectl exec -i $AGENT_POD -n lg-agent -- keyring set cybrid $key
    done
}

main $@
