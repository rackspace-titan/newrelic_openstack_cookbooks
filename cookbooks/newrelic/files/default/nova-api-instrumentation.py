import types
import sys

import newrelic.agent

# First bunch of instrumentation is core stuff we always want to have.

def instrument_nova_wsgi(module):

    newrelic.agent.log(newrelic.agent.LOG_DEBUG,
            'instrument_wsgi()')

    # This is wrapping the WSGI application entry point by
    # capturing it while being passed into server object for
    # use.
    def in_server_init(self, name, application, **kwargs):
        return ((self, name, newrelic.agent.WSGIApplicationWrapper(application)),
                kwargs)

    newrelic.agent.wrap_in_function(module, 'Server.__init__',
            in_server_init)

def instrument_nova_api_openstack_wsgi(module):

    newrelic.agent.log(newrelic.agent.LOG_DEBUG,
            'instrument_nova_api_openstack_wsgi()')

    # This is naming the web transaction after the function which
    # corresponds to the controller/action.

    def name_transaction_resource_dispatch(resource, request, action,
                action_args, **kwargs):
        controller_method = getattr(resource.controller, action)
        name = newrelic.agent.callable_name(controller_method)
        #newrelic.agent.log(newrelic.agent.LOG_VERBOSEDEBUG,
        #        'name_transaction_resource_dispatch() = %s' % name)
        return name

    newrelic.agent.wrap_name_transaction(module, 'Resource.dispatch',
        name=name_transaction_resource_dispatch)

    # Same function but this time recording time spent executing it.

    def name_function_resource_dispatch(resource, request, action,
                action_args, **kwargs):
        controller_method = getattr(resource.controller, action)
        name = newrelic.agent.callable_name(controller_method)
        #newrelic.agent.log(newrelic.agent.LOG_VERBOSEDEBUG,
        #        'name_function_resource_dispatch() = %s' % name)
        return name

    # Now wrapping all the controller methods automatically so don't
    # need to be doing this any more.

    # newrelic.agent.wrap_function_trace(module, 'Resource.dispatch',
    #     name=name_function_resource_dispatch)

    # We also capture error trace at this point. That is unhandled
    # exceptions. The error trace should probably be wrapped around
    # method higher up call chain but below where exceptions are caught
    # and then converted into error response pages. Here will do for now
    # as haven't found better spot yet.

    newrelic.agent.wrap_error_trace(module, 'Resource.dispatch')

    # Wrap the constructor for a resource and instrument automatically
    # any controller object associated with a resource.

    def in_function_resource_init(resource, controller, serializer=None,
            deserializer=None, *args, **kwargs):

        newrelic.agent.log(newrelic.agent.LOG_DEBUG, str(controller))

        # We iterate over all attributes of the controller and for
        # each instamce method we wrap it with a function trace wrapper.
        # Once wrapped that don't have method type so can't wrap twice.

        if not controller:
	    for name in dir(controller):
		object = getattr(controller, name)
		if type(object) == types.MethodType:
		    wrapped = newrelic.agent.FunctionTraceWrapper(object)
		    setattr(controller, name, wrapped)

        return ((resource, controller, serializer=serializer, deserializer=deserializer), kwargs)

    newrelic.agent.wrap_in_function(module, 'Resource.__init__',
            in_function_resource_init)

# Following is where we might start instrumenting optional stuff to
# get a better idea of where time is being spent.

def instrument_nova_api_openstack_views_images(module):

    newrelic.agent.log(newrelic.agent.LOG_DEBUG,
            'instrument_nova_api_openstack_views_images()')

    newrelic.agent.wrap_function_trace(module, 'ViewBuilderV10.build')
    newrelic.agent.wrap_function_trace(module, 'ViewBuilderV11.build')

def instrument_nova_image_service(module):

    newrelic.agent.log(newrelic.agent.LOG_DEBUG,
            'instrument_nova_image_service()')

    newrelic.agent.wrap_function_trace(module, 'BaseImageService.index')

def instrument_nova_image_fake(module):

    newrelic.agent.log(newrelic.agent.LOG_DEBUG,
            'instrument_nova_image_fake()')

    newrelic.agent.wrap_function_trace(module, '_FakeImageService.index')

def instrument_nova_image_glance(module):

    newrelic.agent.log(newrelic.agent.LOG_DEBUG,
            'instrument_nova_image_glance()')

    newrelic.agent.wrap_function_trace(module, 'GlanceImageService.index')

def instrument_nova_image_s3(module):
    f = open('/tmp/blah','w')
    f.write(str(dir(newrelic)) + str(type(newrelic)))
    newrelic.agent.log(newrelic.agent.LOG_DEBUG,
            'instrument_nova_image_s3()')

    newrelic.agent.wrap_function_trace(module, 'S3ImageService.index')

def instrument_glance_client(module):

    newrelic.agent.log(newrelic.agent.LOG_DEBUG,
            'instrument_glance_client()')

    def url_baseclient_do_request(client, method, action, *args, **kwargs):
        return 'http://%s%s/%s' % (client.host, client.doc_root,
                action.lstrip("/"))

    newrelic.agent.wrap_external_trace(module, 'V1Client.do_request',
        library='glance.client', url=url_baseclient_do_request)

    # Could have manually wrapped each method of this class but a
    # quicker way which copes with methods being added or removed
    # is to enumerate over all attributes of the class and if they
    # correspond to an unbound method then wrap it. Note that there
    # is not type object in 'types' module for this type of unbound
    # class method so get them type by looking at type of one of the
    # existing methods. We probably should have this skip special
    # methods like __getattr__() and __setattr_() etc. Should have
    # function which you can give it a class and do all this for
    # you automatically.

    # newrelic.agent.wrap_function_trace(module, 'V1Client.get_images')
    # newrelic.agent.wrap_function_trace(module, 'V1Client.get_images_detailed')
    # newrelic.agent.wrap_function_trace(module, 'V1Client.get_image')
    # newrelic.agent.wrap_function_trace(module, 'V1Client.get_image_meta')
    # newrelic.agent.wrap_function_trace(module, 'V1Client.add_image')
    # newrelic.agent.wrap_function_trace(module, 'V1Client.update_image')
    # newrelic.agent.wrap_function_trace(module, 'V1Client.delete_image')

    unbound_method_type = type(getattr(module.V1Client, 'do_request'))

    for name in dir(module.V1Client):
        object = getattr(module.V1Client, name)
        if type(object) == unbound_method_type:
            object_path = 'V1Client.%s' % name
            newrelic.agent.wrap_function_trace(module, object_path)

def instrument_db_sqlalchemy_api(module):

    newrelic.agent.log(newrelic.agent.LOG_DEBUG,
            'instrument_db_sqlalchemy_api()')

    # This module has heaps and heaps of functions, no classes. Could
    # have enumerated over all of them in style shown commented out
    # below, but can't be bothered to manually enumerate them all. So
    # cheat and iterate over everything in the module and if its is
    # callable and defined in the module then we wrap it.

    # newrelic.agent.wrap_function_trace(module, 'auth_token_get')

    for name in dir(module):
        object = getattr(module, name)
        if callable(object) and hasattr(object, '__module__'):
            if getattr(object, '__module__') == module.__name__:
                newrelic.agent.wrap_function_trace(module, name)

def instrument_compute_api(module):

    newrelic.agent.log(newrelic.agent.LOG_DEBUG,
            'instrument_compute_api()')

    unbound_method_type = type(getattr(module.API, 'get_all'))

    for name in dir(module.API):
        object = getattr(module.API, name)
        if type(object) == unbound_method_type:
            object_path = 'API.%s' % name
            newrelic.agent.wrap_function_trace(module, object_path)

def instrument_api_openstack_auth(module):

    newrelic.agent.log(newrelic.agent.LOG_DEBUG,
            'instrument_api_openstack_auth()')

    unbound_method_type = type(getattr(module.AuthMiddleware, '__init__'))

    for name in dir(module.AuthMiddleware):
        # Don't know whether better to skip '__' methods or not.
        if not name.startswith('__'):
	    object = getattr(module.AuthMiddleware, name)
	    if type(object) == unbound_method_type:
		object_path = 'AuthMiddleware.%s' % name
		newrelic.agent.log(newrelic.agent.LOG_DEBUG,
                    'instrument %s' % object_path)
		newrelic.agent.wrap_function_trace(module, object_path)
