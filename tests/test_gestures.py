from types import SimpleNamespace
from app.hand_gesture import GestureFilter

def palm(x=.5):
    points = [SimpleNamespace(x=x,y=.3) for _ in range(21)]
    points[0].y = .4
    for tip,joint in ((8,6),(12,10),(16,14),(20,18)):
        points[joint].y = .3
        points[tip].y = .15
    return points

def test_swipe_and_cooldown():
    f = GestureFilter()
    assert f.update(palm(.2),1) is None
    assert f.update(palm(.3),1.1) is None
    assert f.update(palm(.45),1.2) == 'next'
    assert f.update(palm(.7),1.3) is None

def test_held_palm_menu_then_selection():
    f = GestureFilter()
    assert f.update(palm(),1) is None
    assert f.update(palm(),1.7) == 'menu'
    assert f.update(palm(),2.9) == 'select'
    assert f.update(palm(),4.5) is None
    f.update(None,5)
    assert f.update(palm(),6) is None

def test_thumbs_up_requires_hold_and_release():
    points = [SimpleNamespace(x=.5,y=.35) for _ in range(21)]
    points[0].y = .5
    for tip,joint in ((8,6),(12,10),(16,14),(20,18)):
        points[tip].y = .42
        points[joint].y = .3
    points[2].y, points[3].y, points[4].y = .35,.25,.15
    f = GestureFilter()
    assert f.update(points,1) is None
    assert f.update(points,1.5) is None
    assert f.update(points,1.9) == 'photo'
    assert f.update(points,3) is None
    f.update(None,4)
    assert f.update(points,5) is None
    assert f.update(points,6) == 'photo'
