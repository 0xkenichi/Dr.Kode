def find(s):
    url = re.findall(regex,s)
    if url:
        return url
    else:
         return False
      