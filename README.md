# Flexom python api
A Python API to control Flexom habitation

## How to install it

```bash
$ pip install git+https://github.com/lchagnoleau/flexom_python_api.git
```

## How to use it

```python
In [1]: from flexom import Flexom
In [2]: f = Flexom(login='yourflexomemail', password='yourpassword')
In [3]: f.set_light(actuatorIds='my_actuatorIds', itId='my_itId', state=1)
```
