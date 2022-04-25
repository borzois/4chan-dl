# 4chan-dl

## Dependencies
- BeautifulSoup4
- requests
```
pip install beautifulsoup4 requests
```

## Usage
```
python3 ./4chan-dl.py [-h] [-d DIRECTORY] [-f FORMAT] [-n NAME] [-q]
                   [--set-default-format | --no-set-default-format]
                   [--set-default-directory | --no-set-default-directory]
                   url
```

## Format
The ```-f``` parameter uses basic string substitution with the % special character

The following variables are supported:
```
%filename  - the image's filename (as uploaded by the poster) 
%id        - the id of the post
%count     - incremented on each image in the thread
%name      - user defined variable, set using -n (useful when quickly downloading threads)
%opid      - the id of the thread
%opname    - the name of the thread (empty char if none)
```
### Formatting examples
#### Creating a default format
```
4chan-dl.py -f "%name/%name_%count" -n "test" --set-default-format -d /4chan/ --set-default-directory
```
Once the default format is set you can simply use
```
4chan-dl.py -n "newthread"
```
on subsequent executions, which will create the following file structure:
```
4chan/
|-newthread/
	|-newthread_1.png
	|-...
```

#### Other examples
```
4chan-dl.py -f "%filename(%id)" 
4chan-dl.py -f "post_%id" 
```
