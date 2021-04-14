# upload_download_service
REST based file upload/download service

Steps to deploy on AWS

Create an AWS instance..
Open the following ports in the security group

```
Custom TCP : 8000
HTTP: 80
HTTPS: 443
```

Launch EC2 instance
Use system_design.pem to access the instance

```
cd /home/pankaj/Documents/aws/pems
ssh -i system_design.pem ubuntu@52.55.169.6
```

Use the following bootstrap script to install softwares

```
sudo apt-get update -y
sudo apt-get install gunicorn -y
sudo apt-get install apache2 -y
```

Install gunicorn
```
sudo apt install gunicorn
```

Download the git project and run gunicorn

```
git clone https://github.com/pankaj-giri/upload_download_service.git

cd upload_download_service

gunicorn --bind 0.0.0.0:8000 app:app
```

Result of running Jmeter stress on a single node of EC2 instance (t2 micro) and with a single worker thread

```
Throughput : 5.5/min
Average: 84625 ms
min: 8819 ms
max: 113420 ms
```
