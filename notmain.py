"""Проект по вебy. Решение задачи коммивояжера. Лана Дзуцева"""
from flask import Flask, render_template, request
import requests
from math import cos, acos, sin, pi, inf
from itertools import permutations

'''Ортодро́мия, ортодро́ма (от др.-греч. «ὀρθός» — «прямой» и
 «δρόμος» — «бег», «путь») в геометрии — кратчайшая линия между двумя точками 
 на поверхности вращения, частный случай геодезической линии.'''
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from classes import Base, Route


# ___________________________________________________________________
def toponym():
    place = 'Владикавказ'
    geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={place}&format=json"
    # Выполняем запрос.
    response = requests.get(geocoder_request)
    if response:
        json_response = response.json()
        toponym = \
            json_response["response"]["GeoObjectCollection"]["featureMember"][
                0][
                "GeoObject"]
        # Полный адрес топонима:
        toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"][
            "text"]
        # Координаты центра топонима:
        toponym_coodrinates = toponym["Point"]["pos"]
        print(toponym_address, "имеет координаты:", toponym_coodrinates)
    else:
        print("Ошибка выполнения запроса:")
        print(geocoder_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")


def get_coords(place='Kyoto'):
    geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={place}&format=json"
    response = requests.get(geocoder_request)
    if response:
        json_response = response.json()
        toponym = json_response["response"]["GeoObjectCollection"] \
            ["featureMember"][0]["GeoObject"]
        toponym_coodrinates = toponym["Point"]["pos"]
        ans = [float(i) for i in toponym_coodrinates.split()]
        ans.reverse()
        return ans
    else:
        print('bad response')


def distance(coord1, coord2):
    y1, x1 = coord1
    y2, x2 = coord2
    y1r, x1r = y1 * pi / 180, x1 * pi / 180
    y2r, x2r = y2 * pi / 180, x2 * pi / 180
    # delta_yr = abs(y1r - y2r)
    delta_xr = abs(x1r - x2r)
    r = 6371.032
    dist1 = r * acos(
        sin(y1r) * sin(y2r) + cos(y1r) * cos(y2r) * cos(delta_xr))
    # dist2 = 6371.032 * acos(
    #     sin(x1) * sin(x2) + cos(x1) * cos(x2) * cos(abs(y1 - y2)))
    # dist3 = r * 2 * asin((sin(delta_yr / 2) ** 2 + cos(y1r) * cos(y2r) * (
    #         sin(delta_xr / 2) ** 2)) ** 0.5)
    # dist = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5 * 111.11
    return dist1


def commivoyage(points, start=False):
    global start_coord
    minn = inf
    path = []
    places = {point: get_coords(point) for point in points}
    if start:
        start_point = points.pop(0)
        start_coord = places[start_point]
    else:
        pass
    for per in permutations(points):
        sequence = list(per)
        if start:
            prev = start_coord
        else:
            prev = places[sequence.pop(0)]
        disst = 0
        while sequence:
            now = places[sequence.pop(0)]
            disst += distance(prev, now)
            prev = now
        if disst < minn:
            minn = disst
            path = per
    # print(path, minn)
    return path, minn


# _______________________________________________________________________
app = Flask(__name__)
points = []

# Подключаемся и создаем сессию базы данных
engine = create_engine('sqlite:///table.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/database')
def show_database():
    data = session.query(Route).all()
    print(data)
    return render_template('landing.html')


@app.route('/')
def main_page():
    return render_template('landing.html')


@app.route('/travel', methods=['POST', 'GET'])
def go():
    if request.method == 'GET':
        return render_template('input.html', points=points)
    if request.method == 'POST':
        # hmm = request.data
        # b = request.args
        print(request.access_route)
        ans = ''
        c = request.form
        print('form', c)
        start = False  # есть ли специально заданная точка старта
        if request.form.get('add'):
            new_point = request.form.get('point')
            if new_point:
                if new_point not in points:
                    points.append(new_point)
                # print(points)
                # return render_template('input.html', points=points)
        if request.form.get('add_start'):
            point = request.form.get('start_point')
            if point in points:
                points.remove(point)

            points.insert(0, point)
            start = True
        if request.form.get('calculate'):
            ans = commivoyage(points, start)
            # return render_template('input.html', points=points, )
        delete = request.form.get('delete')
        if delete:
            points.remove(delete)
        return render_template('input.html', points=points, ans=str(ans))


@app.route('/database', methods=['POST', 'GET'])
def database():
    if request.method == 'GET':
        return render_template('input.html', points=points)
    if request.method == 'POST':
        return render_template('input.html', points=points)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)

# def get_coords(place='Kyoto'):
# #     geocoder_request = f"http://geoc ode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={place}&format=json"
# #     response = requests.get(geocoder_request)
# #     if response:
# #         json_response = response.json()
# #         toponym = \
# #             json_response["response"]["GeoObjectCollection"]["featureMember"][
# #                 0]["GeoObject"]
# #         toponym_coodrinates = toponym["Point"]["pos"]
# #         return reversed(toponym_coodrinates)
# #     else:
# #         print('bad response')
