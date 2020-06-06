from public import ConfigDef

configuration = {
    'server': ConfigDef(shortName="server", required=True, yamlPath="/smb/server", defaultValue=None),
    'username': ConfigDef(shortName="username", required=False, yamlPath="/smb/username", defaultValue=None),
    'password': ConfigDef(shortName="password", required=False, yamlPath="/smb/password", defaultValue=None),
    'port': ConfigDef(shortName="port", required=False, yamlPath="/smb/server", defaultValue=445),
    'connection_timeout': ConfigDef(shortName="connection_timeout", required=False, yamlPath="/smb/server", defaultValue=60),
}