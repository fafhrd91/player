pyramid_vlayer
==============

.. image :: https://secure.travis-ci.org/fafhrd91/pyramid_vlayer.png 
  :target:  https://secure.travis-ci.org/fafhrd91/pyramid_vlayer


Address templates with two parameters, category and name. 
One level directory, folder is category and file in folder is template.
For example 'form:view.vl'. First layer has to be defined:

    >> config = Configurator()
    .. config.include('pyramid_vlayer')
    ..
    .. config.add_vlayer('form', path='./path_to_form_dirctory/form/')

`form` directory can contain any template:

    >> ./form/
    ..   view.pt
    ..   actions.jinja2

Now it is possible to use any of this templates as pyramid renderer path:

    >> config.add_view(
    ..     name='view.html', 
    ..     renderer='form:view.vl')

or 

    >> config.add_view(
    ..     name='actions.html', 
    ..     renderer='form:actions.vl')


Customization
-------------

Any number of layers can be registered. It doesnt require to override 
all templates from category. For example it is possible to override view.pt
with different template:

    >> config.add_vlayer('form', 'custom', path='path_to_form_directory_2/form')

and content of this new directory:

    >> ./another_path/form/
    ..   view.jinja2

Now view `view.html` uses `view.jinja2` template. But `actions.html` stil
uses original template.

Another example, if you want customize `bool` field from ptah.form package
all you need is to create some folder, add it as 'fields' layer, and put
`bool.pt` template to this folder, something like that:

   >> config.add_vlayer('fields', 'custom', 'mypackage:/fields')

and 

   >> .mypackage/fields/
   ..    bool.pt

no need specific template overriding.


Request method
--------------

`pyramid_vlayer` also provides request method `render_tmpl`. It acccepts
path:

   ..  ${structure: request.render_tmpl('form:actions')

`.vl` extension is optional in this case.


License
-------

pyramid_vlayer is offered under the BSD license.
