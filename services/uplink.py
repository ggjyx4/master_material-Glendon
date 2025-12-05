import anvil.server

anvil.server.connect("server_WTGZYTUAVTIF4VPOUR3DYU5F-DJLAASI6MOPSH76S")

test = anvil.server.call('get_material_detail')

print(test)
