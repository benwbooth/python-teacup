HTML Templating DSL for Python.
==============================

A simple HTML templating library that uses a DSL
mini-language. I tried to design it to be similar in feel
to Teacup/CoffeeKup (https://github.com/goodeggs/teacup). I
also took inspiration from jamescasbon's template.py script
(https://gist.github.com/jamescasbon/1461441).

Also includes the md() function for embedding markdown, and an option
for outputting prettified HTML.

Example usage::

    with html:
        with head:
            pass
        with body:
            with p:
                md("This is a **test!**")
            with p:
                text("Another test")
                a("Click here", href="https://google.com")

    print(render())

The python "with" keyword is used to nest HTML tags.
