FROM odoo:13.0
user root
COPY requirements.txt requirements.txt
RUN python3 -m pip install -r requirements.txt