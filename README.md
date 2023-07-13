# low_voltage
Low voltage interface : Low PowerSupply HMP4040

## Developer instructions

Local installation: 

```
conda create -n low_voltage python=3.9
conda activate low_voltage
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements/local.txt
python3 -m pip install -e .  
```

## Unit tests and linting 
No unit test for hmp.py 

Run Black  --check : 

```commandline
black --check . --exclude _actions 
```

Unit tests: 

```commandline
cd unittests
pytest
```

## Dockerfile
To create centos:low_votage image with necessary packages.

```
docker build -t centos:tedd_dcs_low_voltage .
```

## Docker stack
To  start the mqtt broker

```
cd docker/tedd_low_voltage
docker-compose up -d 
```
