#!/bin/bash

mkdir -p /tmp/uploads
sudo docker run  -p 8000:8000 -v /tmp/uploads/:/app/data -d upload_download_service