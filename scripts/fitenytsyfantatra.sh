#!/bin/bash

set -e

cd $HOME/botjagwar
INTERPRETER=python3.6

if ! ps aux | grep python | grep unknown_language_manager
then
	$INTERPRETER unknown_language_manager.py
fi
