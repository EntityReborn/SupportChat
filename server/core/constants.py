import re

nickre = re.compile("^[-_a-zA-Z0-9]+$")

BADMSG = 1
NEEDNICK = 2
DUPNICK = 3
INVALIDNICK = 4
NOTAUTHD = 5
NEEDPROTO = 6
BADPRTCL = 7
BADLOGIN = 8
NEEDLOGIN = 9
UNKNOWNUSER = 10
BADPASS = 11

errorvals = {
    BADMSG: "Bad or empty message",
    NEEDNICK: "You need to specify a nick before you can chat",
    DUPNICK: "Another client with this nick is already connected",
    INVALIDNICK: "Invalid nick name",
    NOTAUTHD: "Not authorized for this action",
    NEEDPROTO: "You must specify PROTOCOL first",
    BADPRTCL: "Unsupported protocol identifier",
    BADLOGIN: "Bad login info. Must supply login info in <username>:<password> format",
    NEEDLOGIN: "This username is protected by password. Please ADMINLOGIN to use it",
    UNKNOWNUSER: "Username unknown"
}
