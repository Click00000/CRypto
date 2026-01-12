#!/bin/bash
# Install backend dependencies first
cd ../backend
pip install -r requirements.txt
cd ../worker
pip install -r requirements.txt
