#!/bin/bash 
set -o pipefail

source ./agent-vars.sh

main() {
  ./stop
  build_image
  start_container
  docker exec -it $AGENT_CONTAINER bash
}

build_image() {
  docker build -f ./build/Dockerfile -t $AGENT_IMAGE .
}

start_container() {
    docker run -d \
    --name $AGENT_CONTAINER \
    -e "TERM=xterm" \
    -v $(pwd):/agent \
    --restart always \
    --entrypoint "sh" \
    $AGENT_IMAGE \
    -c "sleep infinity"

    # Replicate keyring values into container keyring
    keynames=("openaiapi" "mistralapi" "tavilyapi" "langchainapi" "newjodybotpwd")
    for key in "${keynames[@]}" ; do
      echo $(keyring get cybrid $key) 	\
	| docker exec -i $AGENT_CONTAINER keyring set cybrid $key
    done

    # unlock poetry & initialize
    docker exec $AGENT_CONTAINER bash -c "rm -f poetry.lock; poetry update"

    # start jwt-this & update Conjur authn-jwt endpoint w/ signing keys
    docker exec $AGENT_CONTAINER bash -c "cd conjur-setup; ./1-start-jwt-this.sh; ./2-config-jwt-authn.sh"
}

main $@
