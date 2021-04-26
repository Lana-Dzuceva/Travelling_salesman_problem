"""Проект по вебу. Решение задачи коммивояжера. Лана Дзуцева"""
from project.data import db_session
from project.data.routs import Route
from flask import Flask, render_template, request
import requests
from math import cos, acos, sin, pi, inf
from itertools import permutations

'''Ортодро́мия, ортодро́ма (от др.-греч. «ὀρθός» — «прямой» и
 «δρόμος» — «бег», «путь») в геометрии — кратчайшая линия между двумя точками 
 на поверхности вращения, частный случай геодезической линии.'''


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
        try:
            json_response = response.json()
            toponym = json_response["response"]["GeoObjectCollection"] \
                ["featureMember"][0]["GeoObject"]
            toponym_coodrinates = toponym["Point"]["pos"]
            ans = [float(i) for i in toponym_coodrinates.split()]
            ans.reverse()
            return ans
        except Exception:
            return 0
    else:
        return 0


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
    return path, minn


def get_simple_disstance(points):
    ans = 0
    prev = points[0]
    for i in points[1:]:
        ans += distance(get_coords(prev), get_coords(i))
        prev = i
    return ans


def get_key_for_value(value, dict):
    for k, v in dict.items():
        if v == value:
            return k
    return None


# ______________________________________________________________________________
app = Flask(__name__)
points = []
coords = {}
db_session.global_init("db/routs.db")
db_sess = db_session.create_session()
ans = ['', '']


@app.route('/')
def main_page():
    return render_template('landing.html')


@app.route('/travel', methods=['POST', 'GET'])
def go():
    global ans
    if request.method == 'GET':
        return render_template('input.html', points=points, ans=ans)
    if request.method == 'POST':
        # hmm = request.data     b = request.args
        # print(request.access_route)
        my_form = request.form
        print('form', my_form)
        start = False  # есть ли специально заданная точка старта
        if my_form.get('add'):
            new_point = my_form.get('point')
            if new_point:
                temp_coord = get_coords(new_point)
                if temp_coord:
                    if temp_coord not in coords.values():
                        points.append(new_point)
                        coords[new_point] = temp_coord

        if my_form.get('add_start'):
            point = my_form.get('start_point')
            temp_coord = get_coords(point)
            if temp_coord:
                key = get_key_for_value(temp_coord, coords)
                if key:
                    points.remove(key)
                points.insert(0, point)
                coords[point] = temp_coord
                start = True
        if my_form.get('calculate'):
            ans = commivoyage(points, start)
        delete = my_form.get('delete')
        if delete:
            points.remove(delete)
        if my_form.get('open_add'):
            return render_template('input.html', points=points, ans=str(ans),
                                   add=True)
        if my_form.get('add_to_database'):
            global db_sess
            route = Route()
            author = request.form.get('author')
            if not author:
                author = 'Stranger'
            route.author = author
            title = request.form.get('title')
            if not title:
                title = ' '.join(ans[0])
            print(ans)
            route.title = title
            route.path1 = ' '.join(ans[0])
            route.len1 = ans[1]
            db_sess.add(route)
            db_sess.commit()
        if ans != ['', '']:
            return render_template('input.html', points=points,
                                   ans=str(ans))
        return render_template('input.html', points=points)


@app.route('/len_of_path', methods=['POST', 'GET'])
def func():
    global ans
    if request.method == 'GET':
        if ans != ['', '']:
            return render_template('simple_input.html', points=points,
                                   ans=str(ans))
        return render_template('simple_input.html', points=points)
    if request.method == 'POST':
        my_form = request.form
        print('form', my_form)
        if my_form.get('add'):
            new_point = my_form.get('point')
            if new_point:
                temp_coord = get_coords(new_point)
                if temp_coord:
                    if temp_coord not in coords.values():
                        points.append(new_point)
                        coords[new_point] = temp_coord

        if my_form.get('calculate'):
            ans = get_simple_disstance(points)

        delete = my_form.get('delete')
        if delete:
            points.remove(delete)
        if ans != ['', '']:
            return render_template('simple_input.html', points=points,
                                   ans=str(ans))
        return render_template('simple_input.html', points=points)


@app.route('/database', methods=['POST', 'GET'])
def database():
    global db_sess
    gods_path = db_sess.query(Route).all()
    if request.method == 'GET':
        return render_template('database.html',
                               trips=gods_path)
    if request.method == 'POST':
        author = request.form.get('author')
        if author:
            return render_template('database.html',
                                   trips=filter(lambda x: x.author == author,
                                                gods_path))
        title = request.form.get('title')
        if title:
            return render_template('database.html',
                                   trips=filter(lambda x: x.title == title,
                                                gods_path))
        if request.form.get('date'):
            return render_template('database.html',
                                   trips=sorted(gods_path,
                                                key=lambda x: x.created_date))
        if request.form.get('how_long'):
            return render_template('database.html',
                                   trips=sorted(gods_path,
                                                key=lambda x: x.len1))
        return render_template('database.html',
                               trips=gods_path)


def main():
    global db_sess
    route = Route()
    route.title = 'wertyuikjhgf'
    route.author = 'qwerty'
    route.len1 = 6748
    db_sess.add(route)
    db_sess.commit()
    for i in db_sess.query(Route).all():
        print(i.title)


if __name__ == '__main__':
    # main()
    # port = int(os.environ.get("PORT", 5000))
    # app.run(host='0.0.0.0', port=port)
    app.run(host='127.0.0.1', port=8080)

# app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
