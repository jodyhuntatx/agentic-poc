#!/usr/bin/bash

source ../vars.sh

main() {
  install_python_libs
 exit
  # upgrade pip
  python3 -m pip install --upgrade pip
  build_llama_cpp
  download_model_from_hf
  echo
  echo
  echo "Log out and log back in again for correct env settings."
  echo
  echo
  echo
}

#########################
build_llama_cpp() {
  echo
  echo "Runtime ~20:00"
  time CMAKE_ARGS="-DGGML_CUDA=on	\
	  		-DCUDA_PATH=/usr/local/cuda-12.2 \
	  		-DCUDAToolkit_ROOT=/usr/local/cuda-12.2	\
			-DCUDAToolkit_INCLUDE_DIR=/usr/local/cuda-12/include	\
		       	-DCUDAToolkit_LIBRARY_DIR=/usr/local/cuda-12.2/lib64"	\
			FORCE_CMAKE=1 pip install llama-cpp-python --no-cache-dir
}

#########################
download_model_from_hf() {
  # model_url="https://huggingface.co/lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF/resolve/main"
  # model_name=Meta-Llama-3.1-8B-Instruct-Q5_K_M.gguf
  # model_url="https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main"
  # model_name="Llama-3.2-3B-Instruct-Q5_K_L.gguf"
  #model_url="https://huggingface.co/bartowski/Mistral-Nemo-Instruct-2407-GGUF/resolve/main"
  #model_name=Mistral-Nemo-Instruct-2407-Q5_K_M.gguf
  #model_url=https://huggingface.co/AbLoGa/Chat-Mistral-7b-openorca-q4-gguf/resolve/main
  #model_name=mistral-7b-openorca.gguf2.Q4_0.gguf
  model_url=https://huggingface.co/prithivMLmods/Llama-Chat-Summary-3.2-3B-GGUF/resolve/main
  model_name=Llama-Chat-Summary-3.2-3B.Q5_K_M.gguf
  if ! [ -f $MODEL_DIR/$model_name ]; then
    echo "Downloading LLM: $model_name..."
    wget $model_url/$model_name
    mkdir -p $MODEL_DIR
    mv $model_name $MODEL_DIR
  else
    echo "LLM exists in models directory - skipping download."
  fi
}

#########################
install_python_libs() {
  echo
  echo "Runtime ~2:20"
  echo
  time pip3 install pandas numpy torch scikit-learn joblib notebook ipywidgets
  echo
  echo "Runtime ~20 seconds"
  echo
  time pip3 install -U 			\
	  	langchain		\
	  	langchain_community     \
                langchain_huggingface   \
		langchain_core		\
		langchain_experimental
  time pip3 install -U			\
		duckduckgo-search	\
		eventregistry
  time pip3 install -U			\
	  	langgraph		\
		langsmith		\
		langchain_openai	\
		langchain_anthropic	\
		langchain_mistralai	\
		tavily-python		\
		kubernetes		\
		mysql-connector-python
echo
}

main "$@"
