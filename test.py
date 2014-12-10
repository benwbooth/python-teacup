#!/usr/bin/env python3
from teacup import *

with html:
    with head:
        pass
    with body:
        with p:
            md("""This is a **test!**""")
        with p:
            text("Another test")
            a("Click here", href="https://google.com")

#print(render(pretty=False))
print(render())
