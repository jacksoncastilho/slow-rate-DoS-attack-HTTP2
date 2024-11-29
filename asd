#!/bin/bash

# Lista de renomeações
declare -A files=(
  ["completepostheader.py"]="complete_post_header.py"
  ["connectionpreface.py"]="connection_preface.py"
  ["getzerowindow.py"]="get_zero_window.py"
  ["incompleteheader.py"]="incomplete_header.py"
)

# Renomear arquivos
for old_name in "${!files[@]}"; do
  new_name="${files[$old_name]}"
  if [ -f "$old_name" ]; then
    mv "$old_name" "$new_name"
    echo "Renomeado: $old_name -> $new_name"
  else
    echo "Arquivo não encontrado: $old_name"
  fi
done

