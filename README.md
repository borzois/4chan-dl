# 4chan-dl

## Dependencies
- beautifulsoup4
- requests
```
pip install beautifulsoup4 requests
```

## Usage
```
python3 ./4chan-dl.py [-h] [-f FORMAT] [-n NAME] [-q | --quiet | --no-quiet] [-w WATCH]
                   [--set-default-directory | --no-set-default-directory]
                   [--set-default-format | --no-set-default-format]
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
4chan-dl.py -f "~/Downloads/4chan/%name_%opid/%name_%count" -n "test" --set-default-format
```
Once the default format is set you can simply use
```
4chan-dl.py -n "newthread"
```
on subsequent executions, which will create the following file structure:
```
4chan/
|-newthread_66666666/
	|-newthread_1.png
	|-...
```

#### Other examples
```
4chan-dl.py -f "~/Pictures/%filename(%id)" 
4chan-dl.py -f "post_%id" 
```
