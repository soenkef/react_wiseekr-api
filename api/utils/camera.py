# in oui liegt ein script, das die OUI-Listen von verschiedenen Anbietern zusammenführt

# Liste aller bekannten Kamerahersteller
camera_manufacturers = [
    "Abron", "ACESEE", "ACTi", "Acumen", "AirLive", "AKSILIUM", "AlfaVision", "AltCam", "Alteron", "AMATEK",
    "Amovision", "Arax", "Arecont Vision", "AtiS", "Aver", "Avers", "AVTECH", "Axis", "AXYCAM",
    "Bessky", "Beward", "Boavision", "BOLID", "BrickCom", "BSP Security",
    "CMD", "ComOnyX", "Compro", "Corum", "CTV",
    "D-Link", "Dahua", "DiGiVi", "DIVISAT",
    "EasyN", "Elex", "Eneo", "ESVI", "Etrovision", "EverFocus", "eVidence", "Expert",
    "EZVIZ",  # günstiger chinesischer Anbieter
    "Falcon Eye", "Fazera", "Foscam",
    "GANZ", "GeoVision", "GINZZU", "Giraffe", "GNS", "Grumant", "Gwsecu",
    "HDMcam", "Hikvision", "HIQ", "Histream", "HiWatch", "Honeywell", "Hunt", "Huviron",
    "iCam", "IDIS", "INFINITY", "INTELLIKO", "InterVision", "IPEYE", "IPneo", "IPS", "IPTRONIC",
    "iRUS", "iTechPRO", "iTS",
    "J2000IP", "Jassun",
    "KEDACOM", "KENO",
    "LG", "LiteTec", "Longse", "LTV",
    "MASTER", "Mastermann", "MATRIXtech", "MBK", "MICRODIGITAL", "Milesight", "MILLENNIUM", "Mobotix",
    "NATURE", "NAVIgard", "Neovista", "NOVIcam", "Novus",
    "OMNY", "ONVIF", "Optimus", "OwlerPro",
    "Panasonic", "Partizan", "PBT", "Pensee", "Pinetron", "Polyvision", "Powertone",
    "PRAXIS", "ProfVideo", "Proto-X", "PROvision", "PROXISCCTV",
    "QBOR", "Qihan", "QTECH",
    "Ratingsecu", "RedLine", "Reolink", "Ring", "ROKA", "RVi",
    "SafeTech", "SAMSUNG", "Santrin", "SANYO", "Sarmatt", "Sateko", "Satvision", "SECTEC",
    "Smartec", "SNR", "Solkorn", "SOWA", "Spacetechnology", "SpezVision", "SpyG", "SPYMAX",
    "StarDot", "Sunell", "SVN", "SVPlus",
    "Tantos", "Target", "TBTEC", "Tenvis", "Telenova", "Tiandy", "Tigris", "TRENDnet", "TRUEN",
    "Umbrella", "Uniview",
    "VEACAM", "Vesta", "VidaTec", "ViDigi", "Vidstar", "Viscoo", "VIVOTEK",
    "Wyze",  # weiterer günstiger Anbieter
    "XVI",
    "Yudor",
    "ZAVIO", "ZKTeco",
    "3S"
]

additional_budget_manufacturers = [
    "Xiaomi",
    "YI Technology",
    "TP-Link Tapo",
    "Imou",
    "Meross",
    "Tenda",
    "Sricam",
    "SV3C",
    "Zosi",
    "Victure",
    "Ctronics",
    "TVT Digital",
    "Tuya"
]

CAMERA_MANUFACTURERS = camera_manufacturers + additional_budget_manufacturers