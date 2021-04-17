def log_api(function):
    def log_function(*args, **kwargs):
        #Get the bearer token from the request posted and validate
        #with Amazon Cognito
        print(f'*****User invoked the {function.__name__} function*****')
        return function(*args, **kwargs)
    
    # Renaming the function name:
    log_function.__name__ = function.__name__
    return log_function