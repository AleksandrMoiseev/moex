# Moscow Exchange
Загрузка данных об облигациях и акциях с сайта Московской биржи.
* [Programming interface to the ISS](https://www.moex.com/a2920)
* [Программный интерфейс к ИСС](https://www.moex.com/a2193)

## Environment setup
```
python -m venv .env
.\.env\Scripts\Activate.ps1
python.exe -m pip install --upgrade pip
pip install -r requirements.txt
```

## Get MOEX bonds and shares data
```
python main.py --date 2024-09-17
```

## Jupiter Notebook
[Juiter](http://jupyter.org/install)
To run the notebook:
```
jupyter notebook
```