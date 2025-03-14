#!/bin/zsh

if [[ -z $1 ]]; then 
	echo 'Perovide aws region ' && exit
fi

if [[ -z $2 ]]; then 
    echo 'Provide folder to work with' && exit
fi

aws_login $1 && pytho3 tf-refactor.py $2
