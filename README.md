# 4chan-dl

## Dependencies
- BeautifulSoup4
- requests
```
pip install beautifulsoup4 requests
```

## Usage
```
python3 ./4chan-dl.py [-h] [-d DIRECTORY] [-f FORMAT] [-n NAME]
                   [--set-default-format | --no-set-default-format]
                   [--set-default-directory | --no-set-default-directory]
                   url
```

### Formatting examples
The ```-f``` parameter uses basic string substitution with the % special character

#### Creating a default format
```
4chan-dl.py -f "%name_%count" -n "test" --set-default-format
```
Once the default format is set you can simply use:
```
4chan-dl.py -n "newname"
```
on subsequent executions

#### Other examples
```
4chan-dl.py -f "%filename(%id)" 
4chan-dl.py -f "4chan_%id" 
```
