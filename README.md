# sejong-WarRooMi
Kakao Talk bot for reservation of Sejong University Cyber War Room

# using sejong login API
- github url : https://github.com/iml1111/SJ_Auth

# setting server
$ python manage.py makemigrations  
$ python manage.py migrate  
$ python manage.py runserver ip:port  

# setting sslserver
$ python manage.py makemigrations  
$ python manage.py migrate  
$ python manage.py runsslserver ip:port --certificate [fullchain.pem path] --key [privkey.pem path]