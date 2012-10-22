pyramid_vlayer
==============

.. image :: https://secure.travis-ci.org/fafhrd91/pyramid_vlayer.png 
  :target:  https://secure.travis-ci.org/fafhrd91/pyramid_vlayer

pyramid_vlayer allows to address templates with two parameters, 
category and name. Also it is possible to use set of directories
for each layer, in that case `pyramid_vlayer` searches templates
in each directory. It allows to override templates without changing
code. For example form library can define layer `field`::

     >> ls ./fields/
     .. bool.pt
     .. file.pt
     ...
     .. textarea.pt

In your application you can override any of this template by defining 
new layer for `field` category::

     >> ls ./myproject/fields/
     .. bool.pt

Usually top level directory is a category and file in directory is template.
For example 'form:view.vl'::

    `form` - layer category
    `view` - template name
    `.vl`  - custom pyramid renderer factory

Layer can to be defined with `add_vlayer` config directive::

    >> config = Configurator()
    .. config.include('pyramid_vlayer')
    ..
    .. config.add_vlayer('form', path='./path_to_form_dirctory/form/')

`form` directory can contain any template::

    >> ./form/
    ..   view.pt
    ..   actions.jinja2

It is possible to use any of this templates as pyramid renderer path::

    >> config.add_view(
    ..     name='view.html', 
    ..     renderer='form:view.vl')

or ::

    >> config.add_view(
    ..     name='actions.html', 
    ..     renderer='form:actions.vl')


Customization
-------------

Any number of layer categories can be registered and any number of
layers can be registered in each category. It doesnt require to override 
all templates from category. For example it is possible to override just 
view.pt template::

    >> config.add_vlayer('form', 'custom', path='path_to_form_directory_2/form')

and content of this new directory::

    >> ./another_path/form/
    ..   view.jinja2

Now view `view.html` uses `view.jinja2` template. But `actions.html` stil
uses original template.

Another example, if you want customize `bool` field from ptah.form package
all you need is to create some folder, add it as 'fields' layer, and put
`bool.pt` template to this folder, something like that::

   >> config.add_vlayer('fields', 'custom', 'mypackage:/fields')

and ::

   >> .mypackage/fields/
   ..    bool.pt


Request method
--------------

`pyramid_vlayer` also provides request method `render_tmpl`. It acccepts
path::

   ..  ${structure: request.render_tmpl('form:actions')

`.vl` extension is optional in this case.


pvlayer
-------

...


License
-------

pyramid_vlayer is offered under the BSD license.
