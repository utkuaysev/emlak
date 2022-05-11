import re

txt = "2313|42342|5435|54345|534|213123123|123123|2"
x = re.search("([0-9]*\|[0-9]+){4,}", txt)
if x == None or len(x.group(0)) != len(txt):
    print("nonematch")
else:
    print(x.group(0))
