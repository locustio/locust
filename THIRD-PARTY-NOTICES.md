# Third-Party Notices

Locust uses third-party software components. This file lists components that are
integrated at the source level (where Locust code closely couples to their APIs)
along with their license attributions.

## sphinx-markdown-builder

`docs/_ext/llms_txt.py` uses `sphinx_markdown_builder.translator.MarkdownTranslator`
(via a minimal builder proxy) to convert Sphinx doctrees to Markdown for the
auto-generated `llms.txt` / `llms-full.txt` files.

- Source: https://github.com/liran-funaro/sphinx-markdown-builder
- License: MIT

```
The MIT License (MIT)

Copyright (c) 2023-2026, Liran Funaro.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
```
