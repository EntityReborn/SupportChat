[general]
    servername = string(default="Server")
    welcome = string(default="Welcome to the server")
    port = integer(default=6636)

[users]
    [[__many__]]
        fullname = string()
        password = string()
        isadmin = boolean(default=False)
