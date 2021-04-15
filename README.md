# upload_download_service

REST based file upload/download service

## Upload Workflow
1. User uploads a file from the app or the browser. 
2. The front end application - android, ios, or js, will generate an MD5 hash of the file, and the file will be streamed on the wire
3. The upload service, will download the file, to its local drive, and compute the checksum, and if the input checksum and the computed checksum match, an upload success is sent back to the client, else the client will need to retry upload.

## Download Workflow


## Architecture
The architecture uses a load balancer to distribute load across upload/download workers which are geographically distributed EC2 instances running the service.

We could use a multi-level load balancer, to route majority of the traffic to the US region, when requests are made from the US region, and the remaining traffic to closest region.

While this architecture, definitely improves availability and reliability of the service, but during the times when there is a surge of traffic, and all the workers are busy servicing the requests, there is no way to dynamically add more workers to cater to the surge.

This is where AutoScaling groups may help out.

![upload_download_service](architecture/service_architecture.jpg?raw=true)

<i>Other considerations :</i>

* How will SQL db scale - for say about a 100M requests per month? Is sharding required here?
* We may need to consider replication of S3 buckets to cater to performance
* Is there a need to perform caching?

## Storage and RPS calculations

## Model
![upload_download_service](architecture/sql_er_diagram.jpg?raw=true)



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
sudo apt-get install apache2 -y
sudo apt-get install gunicorn -y
sudo apt-get -y install python3-pip
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

Result of running Jmeter stress on a single node of EC2 instance (t2 micro) and with 3 worker threads

```
Throughput : 10/min
Average: 44635 ms
min: 5007 ms
max: 114526 ms
```

Result of running Jmeter stress on a 2 EC2 instances behind a load balancer.. each worker configuration same as the test in the single instance.

```
Throughput : 39.6/min
Average: 12516 ms
min: 3256 ms
max: 28743 ms
```
