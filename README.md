#CVEWarn

https://github.com/theovgr9/CVEWarn.git

CVEWarn is offering a monitoring service about your potentials vulnerabilities which impact your information system. Windows & Linux agents are deployed on operating system and send softwares data to the monitoring server. Thanks to an API, server is searching about CVE which matching with customer data software. The correlation about these two parts are sent to each individual customer dashboard. 

This tutorial explain how to deploy the server on a minimal configuration machine.

## Pré-requis

- Installation de Python3 (https://www.python.org/)
- Installation de pip3 (installé avec Python3)

## Installation


Install the git repository

```sh
git clone https://github.com/theovgr9/CVEWarn.git
```

Install the dependencies

```sh
cd ProjetCyber2
pip3 install -r requirements.txt
```

## Launch the server


Linux : 
```sh
python3 main.py
```

Windows : 

```sh
py main.py
```

Server is running on http://127.0.0.1:80 or http://<your_ip>:80

## License

Distributed under the MIT License. See `LICENSE.txt` for more information.


