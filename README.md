Project for the <i>'Cloud Computing'</i> course. Please, check the [Documentation](Documentation.pdf) for a complete view. 

## Project Specifications
Develop a distributed file storage system based on Ceph. The file storage must expose a REST interface through which external users can perform the following operations:
- Retrieve the list of files currently stored in the system
- Delete a file
- Upload / Download a file
- Shows current statistics on the status of the cluster

The application must be composed of two layers:
- Frontend layer, exposing a REST interface and receiving requests from clients
- Backend layer, exploiting the librados python library in order to interact with a ceph-mon module already deployed in a juju container
A different instance of the backend layer must be deployed on each of the three ceph-mon modules that are part of our installation.

## Architectural Design
The design of the application follows a Service-Oriented Architecture approach; each module exposes a REST interface. We exploit such approach to have a synchronous communication between Client and Server.
The Frontend/Load Balancer tier receives HTTP requests from clients and forwards them to the REST API exposed by the Backend module, which is then in charge of interacting with the Ceph monitor in order to provide an answer.
We deployed a Load Balancer module that acts as dispatcher of clients’ requests. This module is in charge of balancing the requests between the various instances of Backend in order to increase resource utilization and ensure scalability.
Each time a request is received, the Load Balancer retrieves the list of Backend instances available at that moment from a MySQL database, which stores their IPs. This MySQL works as a Shared Storage tier and thanks to it we could easily update the state of the cluster, adding or removing Backend modules, to handle run time changes in the deployment’ state.
We could easily deploy more Load Balancer instances that, by interacting with the MySQL database, would always share the same view of the Backend cluster.

## Frontend Design
We provide the following methods:
- GET /objects - to retrieve the list of the files
- DELETE /objects/filename - to remove a specific file
- POST /objects - to create a new file (the data of the file is included in the payload of the request)
- GET /objects/filename - to retrieve a specific file
- GET /status - to retrieve the current statistics of the cluster

# [For the Professor]

We will first illustrate how to test the application in the cluster and then 
explain how to install all the required modules and file needed to replicate 
the installation.

## How to Test

We already have a **Load Balancer** and a **MySQL** container up and running.

To test the application we just need to run the instances of the backend 
deployed on each **Ceph-mon Module** and then run the **Client** script.

**Ceph-mon**
* On VM `172.16.3.219`
  ```sh
  lxc exec juju-a6d2c6-1-lxd-0 /bin/bash
  python3 api.py
  ```
* On VM `172.16.3.228`
  ```sh
  lxc exec juju-a6d2c6-2-lxd-2 /bin/bash
  python3 api.py
  ```
* On VM `172.16.3.199`
  ```sh
  lxc exec juju-a6d2c6-3-lxd-1 /bin/bash
  python3 api.py
  ```
  
**Client**
* On VM `172.16.3.168`
  ```sh
  python3 ceph-client/client.py
  ```
  
## How to Replicate the Installation

The installation is composed of various modules.

**MySQL Database**

We deployed this module on the VM `172.16.3.231`. 
Such IP is hardcoded into **LB_api.py**. 
Edit it with the IP of the machine where you 
deploy the MySQL module.
1. Deploy a container with MySQL exposing port `3306`
   ```sh
   docker pull mysql/mysql-server
   docker run -p 3306:3306 --name=mysql -d mysql/mysql-server
   ```
2. Change the password
   ```sh
   docker logs mysql 2>&1 | grep GENERATED
   docker exec -it mysql bash
   mysql -u root –p
   ALTER USER 'root'@'localhost' IDENTIFIED BY 'password';
   use mysql;
   update user set host='%' where host='localhost' AND user='root';
   FLUSH PRIVILEGES;
   ```
3. Create the database
   ```sh
   CREATE DATABASE ipaddresses;
   CREATE TABLE IF NOT EXISTS `ipaddresses`.`addresses` ( `containerAddress` VARCHAR(20) NOT NULL ,`address` VARCHAR(20) NOT NULL ,PRIMARY KEY (`containerAddress`) )ENGINE = InnoDB;
   INSERT INTO `ipaddresses`.`addresses` VALUES ("252.3.219.108", "172.16.3.219");
   INSERT INTO `ipaddresses`.`addresses` VALUES ("252.3.228.146", "172.16.3.228");
   INSERT INTO `ipaddresses`.`addresses` VALUES ("252.3.199.60", "172.16.3.199");
   ```
   
**Load Balancer**

We deployed this module on the VM `172.16.3.231`. 
Such IP is hardcoded into **FE_client.py**. 
Edit it with the IP of the machine where you 
deploy the Load Balancer module.
Other instances of this module may be easily deployed.
1. ```sh
   mkdir load-balancer
   cd load-balancer
   ```
2. Create `api.py` file and paste into it the content of `LB_api.py`
3. Create `requirements.txt` file and write in it
   ```sh
   Flask==0.10.1
   mysqlclient
   ```
4. Create `Dockerfile` file and write in it
   ```sh
   FROM python:3-alpine

   WORKDIR /app
   COPY . .

   RUN apk add --update --no-cache mariadb-connector-c-dev \
       && apk add --no-cache --virtual .build-deps \
           mariadb-dev \
           gcc \
           musl-dev \
       && pip install mysqlclient==1.4.6 \
       && apk del .build-deps
   
   RUN pip install -r requirements.txt
   
   EXPOSE 8080
   
   ENTRYPOINT ["python3"]
   
   CMD [ "api.py"]
   ```
5. Build and Run the container exposing port `8080`
   ```sh
   docker build -t load-balancer .
   docker run -p 8080:8080 -d load-balancer
   ```
   
**Ceph-mon**

We need to do port-forwarding for each _juju container_ hosting e _ceph-mon_ module.
To do it, on each machine we do
```sh
iptables -t nat -A PREROUTING -p tcp -i eth0 --dport 8080 -j DNAT --to-destination <juju container IP>:8080
```
Then, put `BE_api.py` and `BE_server.py` in each _juju container_
    
**Client**

Put `FE_client.py` in the machine where you want to run the client
