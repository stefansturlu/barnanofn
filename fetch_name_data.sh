#!/bin/bash

mkdir name_files

curl https://hagstofan.s3.amazonaws.com/media/public/names.json > name_files/hagstofan.json

python -c "from names import scrape_all_names; scrape_all_names()"
