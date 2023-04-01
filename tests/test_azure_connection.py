from azure.appconfiguration.provider import load
from dotenv.main import load_dotenv
import os

load_dotenv()

connection_string = os.environ["AZURE_APPCONFIG_CONNECTION_STRING"]
config = load(connection_string=connection_string, )

config = load(connection_string=connection_string)
panel_noct = config['panel:NOCT']
P_STC = config['panel:P_STC']
panel_alpha = config['panel:alpha']
panel_area = config['panel:area']
I_P_mod = config['panel:I_P_mod']
I_SC_mod = config['panel:I_SC_mod']
