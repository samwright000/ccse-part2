from website import create_app # this is import a function from the __init__ script 

app = create_app()#website object 

if __name__ == '__main__':
    app.run(debug=True)#host='0.0.0.0'. This starts the service, debug is = to true while editing but this would be removed when launched. 