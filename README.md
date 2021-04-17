# Upload/Download Service

Problem statement​ : A new microservice needs to be designed which handles all file uploads
(imports) and downloads (exports). The APIs exposed by this service will be consumed by the
browser-based and native applications of the platform to provide this functionality. The service
should be hosted on the cloud and should be a secured endpoint. It should seamlessly scale
upto a max concurrency of 1000 simultaneous uploads / downloads to begin with. The solution
should be future proof and adding more capacity should be simple. The SLI for this service
should be:

<i>Latency to upload / download <= 4 seconds for 5 MB of file size for 95pc of customers (last mile
bandwidth being a limiting factor on the user’s side, we can assume a steady state good
connectivity on the last mile).</i>

## Tech Stack
* Python - Flask + Blueprint APIs
* Gunicorn - WSGI Server
* DB - ElasticSearch for metadata, Redis Cache
* AWS S3 for file storage
* AWS EC2 for hosting webserver
* Route 53, Application Load Balancer

## Architecture
Architecture uses Route 53 to route the requests across regions.

Every region is catered to by a set of AZs sitting behind a Load Balancer. The LB, routes the requests to appropriate AZ, depending on proxmity of the request, latency and the existing load on the AZ. 

Once routed into the AZ, request served by EC2 instances which are managed by an auto-scaling group. This is used to scale out, when there is a surge in number of requests (time based), and scale down when the demand is low.

Service is split to handle uploads and downloads in separate nodes. The reason being the following..

* Uploads have to go through disk writes, which are going to be slower, than reads which may be served from the cache
* A node can handle only limited number of connections, and if the nodes are busy serving up writes, the reads which can happen concurrently and very quickly will get unnecessary blocked
* Its easier to scale out or down reads and writes independently, depending on demand

![upload_download_service](architecture/service_architecture2.jpg?raw=true)

## Storage and RPS calculations

### File Storage Requirements
```
Assumptions :

Requests per month : 10M 
50% split of reads/writes
Average File size : 5MB
Long term storage requirement : 10 years

File storage required : 5M * 5MB * 12 months * 10 years = 3000 TB
```

### Bandwidth requirements
```
Requests per month : 10M 
Average File size : 5MB

RPS : 10M/(30*24*60*60) = ~0.5 RPS
Bandwidth : 0.5 * 5MB = ~2.5MBps for both uploads and downloads

Sometimes a burst of 1000 requests to be accommodated.. in such case the bandwidth required would be : 1000 * 5MB = 5 GBPS
```


### Model
![upload_download_service](architecture/sql_er_diagram.jpg?raw=true)

### DB Storage Requirements

```
Assumptions :

Number of Users : 10 M
Number of active users per month : 1 M
Average number of files/user : 500

Size of user table : ~100 bytes * 10M  = ~1GB
Size of file table : ~200 bytes * 10M * 500  = ~ 1TB

```

Can use either a NoSql or SQL db, and shard by User_ID.


## APIs
1. Upload file - This api allows upload of a file from the client application or web browser.

```
URL : /upload_download_service/upload

Method : POST

Data Params :
Payload containing the key 'file' and value as the byte stream and the MD5 hash of the file

Success Response:
Code : 200
Content : { 'name' : <filename> }

Error Response:
Code : 403
Content : { 'error' : "client credentials invalid" }

or 

Error Response:
Code : 409
Content : { 'error' : "checksum failed - please attempt reuploading" }

or

Error Response:
Code : 413
Content:  { 'error' : "Document file size is too large" }

```


2. Download file - This api allows user to select a file for download

```
URL : /upload_download_service/<fname>/<uid> 

Method : GET

URL Params :
Name of the file and the user_id

Success Response:
Code : 200
Content : { 'name' : <filename> }

Error Response:
Code : 403
Content : { 'error' : "client credentials invalid" }

```

## Upload flow
![upload_download_service](architecture/upload_flow.jpg?raw=true)

1. User uploads a file from the app or the browser. 
2. The front end application - android, ios, or js, will generate an MD5 hash of the file, and the file will be streamed on the wire
3. The upload service will compute  the file's checksum, and if the input checksum and the computed checksum match, an upload success is sent back to the client, else the client will need to retry upload.
4. If successfully uploaded, the service, makes an entry for the file in the ```File``` table, and then push the content to S3

## Download flow
![upload_download_service](architecture/download_flow.jpg?raw=true)

1. User sees a list of files uploaded, when he logs in 
2. User selects the file for download
3. Back end will check if the file is available in the cache, if yes, then the file is served from the cache
4. If file is not present in the cache, the service, fetches the metadata from DB, gets the file from S3 and updates the cache, and returns the file


## API security
![upload_download_service](architecture/api_security.jpg?raw=true)


<i>Other considerations :</i>

* How will SQL db scale - for say about a 100M requests per month? Is sharding required here?
Yes sharding on User ID may help here, and with that we could switch over to a NoSql db - need to check how to draw the ER diagram for a NoSql db.

* We may need to consider replication of S3 buckets to cater to performance
* Is there a need to perform caching?
Yeah, this will definitely help with downloads, where, a server could hit the cache, before it turns to the db or s3. That will enormously help with performance. 
Need to add cache layer to the architecture.
* Add information about Autoscaling Groups and think what can be done better.
* Logging - logging access information - who accessed which doc, how much time for upload, number of attempts, errors.
* You cannot set up ELBs across regions. You will need route 53 to do cross region requests.


Further reading:
https://aws.amazon.com/blogs/architecture/scale-your-web-application-one-step-at-a-time/


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
