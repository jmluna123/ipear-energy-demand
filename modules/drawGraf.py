from matplotlib.colors import ListedColormap, rgb2hex
from PIL import Image, ImageFont, ImageDraw
from IPython.display import display, HTML
import matplotlib.pyplot as plt
import rioxarray as rx
import uuid
import math

# Resumen y Gráficos
plt.style.use("seaborn-whitegrid")

inclination = rx.open_rasterio("files/test_area/test-inclination.tif")
landcover = rx.open_rasterio("files/test_area/test-landcover.tif")
land_60 = rx.open_rasterio("files/test_area/test-landcover_filtered.tif")
crops = rx.open_rasterio("files/test_area/test-crops.tif")
crops_val = crops.values
ground = rx.open_rasterio("files/test_area/test-ground.tif")

cmap = ListedColormap(
    ['ivory', 'turquoise', 'darkgreen', 'orange', 'lavender', 'orange', 'orange', 'red', 'silver', 'lightblue', 'gray'])
cmap1 = ListedColormap(['white', 'gray'])
cmap_crops = ListedColormap(['white', 'orange'])
cmap_ground = ListedColormap(['white', 'gray'])


def show_rad_mean_graph(mean_rad, years=10):
    fig, ax = plt.subplots()

    mean_rad.plot(kind='bar', width=0.70, color='gold', ax=ax, figsize=(12, 6))
    plt.legend(['Irradiancia'])
    plt.title("Irradiancia media en los últimos " +
              str(years) + " años", fontweight='bold')
    plt.ylabel("Irradiancia Wh m-2 día-1")

    for index, value in enumerate(mean_rad):
        ax.text(index - 0.3, value + 2, f'{value:.2f}', )

    plt.show()


def show_Hs_mean_graph(Hs_mean):
    fig, ax = plt.subplots()

    hs_min = Hs_mean.min()
    colors = []
    for value in Hs_mean:
        if value > hs_min:
            colors.append('gold')
        else:
            colors.append('goldenrod')

    Hs_mean.plot(kind='bar', width=0.70, color=colors, ax=ax, figsize=(12, 6))
    plt.legend(['Radiación'])
    plt.title("Promedio de la radiación diaria disponible", fontweight='bold')
    plt.ylabel("Radiación kWh m-2 día-1")

    for index, value in enumerate(Hs_mean):
        ax.text(index - 0.23, value + 0.05, f'{value:.2f}', )

    uid = uuid.uuid1()
    ruta = "static/curvas/" + uid.hex + ".jpg"
    plt.savefig(ruta)
    # plt.show()


def show_temp_mean_graph(mean_temp, years=10):
    fig, ax = plt.subplots()

    temp_min = mean_temp.min()
    colors = []
    for value in mean_temp:
        if value > temp_min:
            colors.append('orange')
        else:
            colors.append('gold')

    mean_temp.plot(kind='bar', width=0.70,
                   color=colors, ax=ax, figsize=(12, 6))
    plt.legend(['Temperatura'])
    plt.title("Temperatura Media en los últimos " +
              str(years) + " años", fontweight='bold')
    plt.ylabel("°C")

    for index, value in enumerate(mean_temp):
        ax.text(index - 0.3, value + 0.3, f'{value:.2f}', )

    uid = uuid.uuid1()
    ruta = "static/curvas/" + uid.hex + ".jpg"
    plt.savefig(ruta)
    # plt.show()


def show_E_elec_graph(E_elec_month):
    fig, ax = plt.subplots()

    E_elec_month.plot(kind='bar', width=0.70,
                      color='cadetblue', ax=ax, figsize=(12, 6))
    plt.title("Promedio de Energía diaria solicitada por la carga",
              fontweight='bold')
    plt.ylabel("Energía diaria kWh/dia")

    for index, value in enumerate(E_elec_month):
        ax.text(index - 0.4, value + 50, f'{value:.2f}', )

    uid = uuid.uuid1()
    ruta = "static/curvas/" + uid.hex + ".jpg"
    plt.savefig(ruta)
    # plt.show()


def show_Y_graph(Y_mean, Y_per_month):
    fig, ax = plt.subplots()

    Y_max = Y_per_month.max()
    colors = []
    for value in Y_per_month:
        if value < Y_max:
            colors.append('lightsteelblue')
        else:
            colors.append('steelblue')

    Y_mean.plot(kind='bar', width=0.70, color=colors, ax=ax, figsize=(12, 6))
    plt.legend(['Y'])
    plt.title("Coeficiente Y", fontweight='bold')
    plt.ylabel("m2")

    for index, value in enumerate(Y_mean):
        ax.text(index - 0.35, value + 15, f'{value:.2f}', )

    uid = uuid.uuid1()
    ruta = "static/curvas/" + uid.hex + ".jpg"
    plt.savefig(ruta)
    # plt.show()


def show_landcover_filter():
    figure, axis = plt.subplots(1, 3, figsize=(20, 5))

    inclination.plot(cmap=cmap1, ax=axis[0])
    axis[0].set_title("Inclinación")

    landcover.plot(cmap=cmap, ax=axis[1])
    axis[1].set_title("Uso de suelo")

    land_60.plot(cmap=cmap, ax=axis[2])
    axis[2].set_title("Uso de suelo filtrado")

    plt.show()


def show_landcover_groups():
    figure, axis = plt.subplots(1, 3, figsize=(20, 5))

    land_60.plot(cmap=cmap, ax=axis[0])
    axis[0].set_title("Uso de suelo")

    crops.plot(cmap=cmap_crops, ax=axis[1])
    axis[1].set_title("Cultivos")

    ground.plot(cmap=cmap_ground, ax=axis[2])
    axis[2].set_title("Esplanada")

    plt.show()


# def show_ground_data():
#     figure, axis = plt.subplots(1, 3, figsize=(20, 5))

#     ground.plot(cmap=cmap_ground, ax=axis[0])
#     axis[0].set_title("Esplanada")

#     temp.plot(ax=axis[1])
#     axis[1].set_title("Temperatura")

#     rad.plot(ax=axis[2])
#     axis[2].set_title("Radiación")

#     plt.show()


css_th = "text-align: center;"
css_td = "text-align: left;"
css_tr = "text-align: center;"

MOD_SIZE = (80, 100)
SPACE = 15


def draw_module(draw, x, y):
    mod_x, mod_y = x + MOD_SIZE[0], y + MOD_SIZE[1]
    lin_x, lin_y = (mod_x - x) / 2 + x, (mod_y - y) / 3 + y

    # conector
    draw.line([(lin_x, y), (lin_x, y - SPACE)], fill=(0, 0, 0))

    # plus
    draw.line([(lin_x, y + 10), (lin_x, lin_y - 10)], fill=(0, 0, 0))
    draw.line([(lin_x - 6, y + 17), (lin_x + 6, y + 17)], fill=(0, 0, 0))

    # mod
    draw.rectangle([(x, y), (mod_x, mod_y)], outline=(0, 0, 0))
    draw.line([(x, y), (lin_x, lin_y)], fill=(0, 0, 0))
    draw.line([(lin_x, lin_y), (mod_x, y)], fill=(0, 0, 0))


def show_modules(N_series, N_paralel):
    im = Image.new('RGB', (
        (MOD_SIZE[0] * N_paralel) + (SPACE * (N_paralel + 2)), (MOD_SIZE[1] * N_series) + (SPACE * (N_series + 2))),
        (255, 255, 255))
    draw = ImageDraw.Draw(im)

    x_init, y_init = SPACE, SPACE
    x, y = x_init, y_init

    for par in range(N_paralel):
        for ser in range(N_series):
            draw_module(draw, x, y)
            y = y + MOD_SIZE[1] + SPACE
        x = x + MOD_SIZE[0] + SPACE
        y = y_init

    # draw.text((100, 100), "N mod Paralelo", fill ="black" , align ="left")
    # im.save('data/dst/pillow_imagedraw.jpg', quality=95)
    display(im)


def mid_point(x_ground, y_ground, x_crop, y_crop, i):
    x_mid, y_mid = (math.ceil((x_ground + x_crop) / 2),
                    math.ceil(((y_ground + y_crop) / 2)))
    is_crop = crops_val[0, y_mid, x_mid]

    # search left
    x, y = (-1, -1)
    if i > 0 and is_crop != 1:
        x, y = mid_point(x_mid, y_mid, x_crop, y_crop, i - 1)
    # search right
    elif i > 0 and is_crop == 1:
        x, y = mid_point(x_ground, y_ground, x_mid, y_mid, i - 1)
    elif is_crop != 1:
        return (x_mid, y_mid)
    else:
        return (-1, -1)

    if x == -1 and is_crop == 1:
        return (-1, -1)
    if x != -1:
        return (x, y)
    return (x_mid, y_mid)
