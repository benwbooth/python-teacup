"""
HTML Templating DSL for Python.

A simple HTML templating library that uses a DSL
mini-language. I tried to design it to be similar in feel
to Teacup/CoffeeKup (https://github.com/goodeggs/teacup). I
also took inspiration from jamescasbon's template.py script
(https://gist.github.com/jamescasbon/1461441).

Also includes the md() function for embedding markdown, and an option
for outputting prettified HTML.

Example usage::

    from teacup import *

    with html:
        with head:
            pass
        with body:
            with p:
                md("This is a **test!**")
            with p({"class":"test"}, id="testme"):
                text("Another test")
                a("Click here", href="https://google.com")

    print(render())

The python "with" keyword is used to nest HTML tags.

"""

import re, sys, mistune, bs4

doctypes = {
  'default': '<!DOCTYPE html>',
  '5': '<!DOCTYPE html>',
  'xml': '<?xml version="1.0" encoding="utf-8" ?>',
  'transitional': '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">',
  'strict': '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">',
  'frameset': '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Frameset//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-frameset.dtd">',
  '1.1': '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">',
  'basic': '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML Basic 1.1//EN" "http://www.w3.org/TR/xhtml-basic/xhtml-basic11.dtd">',
  'mobile': '<!DOCTYPE html PUBLIC "-//WAPFORUM//DTD XHTML Mobile 1.2//EN" "http://www.openmobilealliance.org/tech/DTD/xhtml-mobile12.dtd">',
  'ce': '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "ce-html-1.0-transitional.dtd">',
}

elements = {
  # Valid HTML 5 elements requiring a closing tag.
  # Note: the `var` element is out for obvious reasons, please use `tag 'var'`.
  'regular': """a abbr address article aside audio b bdi bdo blockquote body button
 canvas caption cite code colgroup datalist dd del details dfn div dl dt em
 fieldset figcaption figure footer form h1 h2 h3 h4 h5 h6 head header hgroup
 html i iframe ins kbd label legend li map mark menu meter nav noscript object
 ol optgroup option output p pre progress q rp rt ruby s samp section
 select small span strong sub summary sup table tbody td textarea tfoot
 th thead time title tr u ul video""",

  'raw': 'script style',

  # Valid self-closing HTML 5 elements.
  'void': """area base br col command embed hr img input keygen link meta param
 source track wbr""",

  'obsolete': """applet acronym bgsound dir frameset noframes isindex listing
 nextid noembed plaintext rb strike xmp big blink center font marquee multicol
 nobr spacer tt""",

  'obsolete_void': """basefont frame""",
}

# Create a unique list of element names merging the desired groups.
def merge_elements(*args):
    result = []
    for a in args:
        for element in re.split(r'\s+',elements[a]):
            if element not in result: result.append(element)
    return result

class Ie:
    def __init__(self, doc, startTag=True):
        self.doc = doc
        self.condition = condition
        self.startTag = startTag;
    def __call__(self, condition):
        self.doc.raw("<!--[if {}]>".format(condition))
        self.doc.htmlOutBuffer = "<![endif]-->"
        return Ie(self.doc, self.tagName, False)
    def __enter__(self):
        if self.startTag: raise Exception("No condition was given!")
        else: self.doc.htmlOutBuffer = ''
    def __exit__(self, exception_type, exception_value, traceback):
        self.doc.raw("<![endif]-->")

class Tag:
    def __init__(self, doc, tagName=None, startTag=True):
        self.doc = doc
        self.tagName = tagName
        self.startTag = startTag;
    def __call__(self, *args, **attrs):
        text = ''
        for arg in args:
            if type(arg) is dict:
                attrs.update(arg)
            elif type(arg) in (Ie, Tag, Doc):
                raise Exception("Tags cannot be passed as arguments to other tags (Use \"with\" blocks instead)")
            else:
                text += str(arg)
        self.doc.raw("<{}{}>".format(self.tagName, self.doc.renderAttrs(attrs)))
        self.doc.text(text)
        self.doc.htmlOutBuffer = "</{}>".format(self.tagName)
        return Tag(self.doc, self.tagName, False)
    def __enter__(self):
        if self.startTag: self.doc.raw("<{}>".format(self.tagName))
        else: self.doc.htmlOutBuffer = ''
    def __exit__(self, exception_type, exception_value, traceback):
        self.doc.raw("</{}>".format(self.tagName))
    def __getattr__(self, name):
        return Tag(self.doc, name)
    def __getitem__(self, name):
        return Tag(self.doc, name)

class Doc:
    def __init__(self):
        self.htmlOut = None
        self.htmlOutBuffer = ''

        for tagName in merge_elements('regular', 'obsolete'):
            setattr(self, tagName, Tag(self, tagName))

    def render(self, html=None, pretty=False, *args, **kwargs):
        previous = self.htmlOut + self.htmlOutBuffer
        self.htmlOut = html
        self.htmlOutBuffer = ''
        if pretty: previous = bs4.BeautifulSoup(previous).prettify(*args, **kwargs)
        return previous

    def tag(self, **args):
        return Tag(self, **args)
        
    def ie(self, **args):
        return Ie(self, **args)

    def __getattr__(self, name):
        return self.tag(name)

    def __getitem__(self, name):
        return self.tag(name)

    def renderAttr(self, name, value):
        if value is None: return " {}".format(name)
        if value == False: return ''
        if name == 'data' and type(value) is dict:
            return ''.join(self.renderAttr("data-{}".format(k), v) for k,v in value)

        name = re.sub(r'([A-Z])', lambda x: "-{}".format(x.lower), name)
        if value == True: value = name
        return " {}={}".format(name, self.quote(self.escape(str(value))))

    attrOrder = ['id', 'class']
    def renderAttrs(self, obj):
        result = ''

        # render explicitly ordered attributes first
        for name in self.attrOrder:
            if name in obj:
                result += self.renderAttr(name, obj[name])
                del obj[name]

        # then unordered attrs
        for name, value in obj.items():
            result += self.renderAttr(name, value)

        return result

    def rawTag(self, tagName, contents, **attrs):
        self.raw("<{}{}>".format(tagName, self.renderAttrs(attrs)))
        self.raw(contents)
        self.raw("</{}>".format(tagName))

    def selfClosingTag(self, tag, **attrs):
        self.raw("<{}{} />".format(tag,self.renderAttrs(attrs)))

    def coffeescript(self, fn):
        self.raw("""<script type="text/javascript">(function() {
          var __slice = [].slice,
              __indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; },
              __hasProp = {}.hasOwnProperty,
              __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };
          (#{fn.toString()})();
        })();</script>""")

    def comment(self, text):
        self.raw("<!--{}-->".format(self.escape(text)))

    def doctype(self, type=5):
        self.raw(doctypes[type])

    def text(self, s):
        if self.htmlOut is None:
            raise Exception("Teacup: can't call a tag function outside a rendering context")
        if self.htmlOut is None: self.htmlOut = ''
        self.htmlOut += self.htmlOutBuffer + self.escape(str(s)) if s is not None else ''
        self.htmlOutBuffer = ''

    def raw(self, s):
        if s is None: return
        if self.htmlOut is None: self.htmlOut = ''
        self.htmlOut += self.htmlOutBuffer + str(s)
        self.htmlOutBuffer = ''

    def md(self, *args, **kwargs):
        self.raw(mistune.markdown(*args, **kwargs))

    #
    # Filters
    # return strings instead of appending to buffer
    #

    # Don't escape single quote (') because we always quote attributes with double quote (")
    def escape(self, text):
        return re.sub(r'"', '&quot;',
               re.sub(r'>', '&gt;',
               re.sub(r'<', '&lt;',
               re.sub(r'&', '&amp;', str(text)))))

    def quote(self, value):
        return "\"{}\"".format(value)

    #
    # Binding
    #
    def tags(self): 
        bound = {}
        boundMethodNames = (re.split(r'\s+','coffeescript comment doctype escape raw render renderable script selfClosingTag text md') +
                merge_elements('raw','void','obsolete_void'))

        for method in boundMethodNames:
            def fn(method):
                def fn2(*args, **kwargs):
                    return getattr(Doc, method)(self, *args, **kwargs)
                return fn2
            bound[method] = fn(method)

        for tag in merge_elements('regular','obsolete'):
            bound[tag] = Tag(self, tag)
        
        return bound

for tagName in merge_elements('raw'):
    def fn(tagName):
        def fn2(self, *args, **kwargs):
            return self.rawTag(tagName, *args, **kwargs)
        setattr(Doc, tagName, fn2)
    fn(tagName)

for tagName in merge_elements('void', 'obsolete_void'):
    def fn(tagName):
        def fn2(self, *args, **kwargs):
            return self.selfClosingTag(tagName, **kwargs)
        setattr(Doc, tagName, fn2)
    fn(tagName)

doc = Doc()
for k, v in doc.tags().items():
    setattr(sys.modules[__name__], k, v)

