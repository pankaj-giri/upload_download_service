# upload_download_service
REST based file upload/download service

Steps to deploy on AWS
Launch EC2 instance
Use system_design.pem to access the instance

```
cd /home/pankaj/Documents/aws/pems
ssh -i system_design.pem ubuntu@52.55.169.6
```

Do an update of the system using

```
sudo apt update
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
