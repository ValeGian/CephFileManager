# CC_Ceph_File_Manager

We will first illustrate how to test the application in the cluster and then 
explain how to install all the required modules and file needed to replicate 
the installation.

## How to Test

We already have a **Load Balancer** and a **MySQL** container up and running.

To test the application we just need to run the instances of the backend 
deployed on each **Ceph-mon Module** and then run the **Client** script.

####Ceph-mon
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
####Client
* On VM `172.16.3.168`
  ```sh
  python3 ceph-client/client.py
  ```
  
## How to Replicate the Installation

The installation is composed of various modules.

####MySQL Database
We deployed this module on the VM `172.16.3.231`. 
Such IP is hardcoded into the scripts that interact with this module 
(e.g. the **Load Balancer module**).
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
   
####Load Balancer
We deployed this module on the VM `172.16.3.231`. 
Such IP is hardcoded into the scripts that interact with this module 
(e.g. the **Client module**).
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
####Ceph-mon & Client 
* Put `BE_api.py` and `BE_server.py` in the three ceph-mon modules
* Put `FE_client.py` in the machine where you want to run the client