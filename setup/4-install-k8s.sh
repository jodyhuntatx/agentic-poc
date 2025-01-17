#!/bin/bash

main() {
  install_kubectl
  install_minikube
}

########################
install_kubectl() {
  echo "Installing Kubectl..."
  echo "deb https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
  sudo snap install kubectl --classic
}

########################
install_minikube() {
  echo "Installing Minikube..."
  ARCH=$(uname -m)
  case $ARCH in
    x86_64)
        curl -LO -k https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
        sudo install minikube-linux-amd64 /usr/local/bin/minikube && rm minikube-linux-amd64
        ;;
    aarch64)
        curl -LO -k https://storage.googleapis.com/minikube/releases/latest/minikube-linux-arm64
        sudo install minikube-linux-arm64 /usr/local/bin/minikube && rm minikube-linux-arm64
        ;;
    *)
        echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        echo "!! Unknown machine architecture. Cannot install minikube !!"
        echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        exit -1
  esac
  echo
  echo "Minikube installed"
  minikube version
  echo
}

main "$@"
