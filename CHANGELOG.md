# Changelog

## 3.2.0


* Added Sphinx directive 'swagger-ui' for embedding swagger ui in sphinx docs
* Removed old method to generate single Swagger UI pages
* Implemented new Swagger Layout to disable title bar in embedded UI
* Added new plugins config values
  * babel_js_uri
  * react_dev_js_uri
  * prop_types_js_uri



## 3.1.0

* Support Sphinx 7

## 3.0.0

* Make ``swagger_plugin_for_sphinx.plugin`` private
* Remove ``swagger_plugin_for_sphinx.__version__``
* The module can now be used as the extension name, so instead of using
  ``swagger_plugin_for_sphinx.plugin`` use ``swagger_plugin_for_sphinx``

## 2.0.0

* Support sphinx 6.x
* Add official support for python 3.11
* Remove support for python 3.7
* Remove support for sphinx 4.x and 5.x

## 1.2.0

* Require at least python 3.7.2
* Support sphinx 5.x

## 1.1.0

* internal change from ``os.path`` to ``pathlib``
* Marked the project as stable

## 1.0.0

Initial release
