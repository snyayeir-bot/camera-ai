import json
import numpy as np
import pytest
from app.settings_manager import Settings, validate, ROOT
from app.image_processor import affine_matrix, composite
from app.clothing_manager import ClothingManager
from app.clothing_engine import ClothingEngine
from app.photo_booth import prepare_photo, save_photo

def test_geometry_maps_known_anchors():
    anchors = [[0,0],[1,0],[0,1]]
    targets = np.array([[10,20],[110,40],[-10,220]],np.float32)
    matrix = affine_matrix(anchors,(100,200),targets)
    source = np.array([[0,0,1],[100,0,1],[0,200,1]])
    np.testing.assert_allclose(source@matrix.T,targets,atol=1e-4)

def test_alpha_blend():
    frame = np.full((4,4,3),100,np.uint8)
    asset = np.zeros((4,4,4),np.uint8)
    asset[:,:,:3] = 200
    np.testing.assert_array_equal(composite(frame,asset,np.eye(2,3)),frame)
    asset[:,:,3] = 255
    assert np.all(composite(frame,asset,np.eye(2,3)) == 200)

def test_settings_roundtrip(tmp_path):
    settings = Settings(tmp_path/'config.json')
    data = settings.data | {'language':'km','clothing_scale':1.2}
    settings.save(data)
    assert Settings(settings.path).data == data

def test_overlay_clips_at_frame_edge():
    frame = np.zeros((10,20,3),np.uint8)
    asset = np.full((6,6,4),255,np.uint8)
    matrix = np.array([[1.,0.,18.],[0.,1.,8.]])
    result = composite(frame,asset,matrix)
    assert np.count_nonzero(result[:,:,0]) == 4
    matrix[:,2] = [30,30]
    np.testing.assert_array_equal(composite(frame,asset,matrix),frame)

@pytest.mark.parametrize('data',[{'camera':-1},{'language':'bad'},{'sensitivity':2},{'mirror':'yes'},{'photo_dir':''}])
def test_bad_settings(data):
    with pytest.raises(ValueError):
        validate(data)

def test_catalog_and_render():
    catalog = ClothingManager(ROOT/'assets/clothes')
    assert len(catalog.items) >= 7
    frame = np.full((720,1280,3),100,np.uint8)
    points = np.zeros((33,4),np.float32)
    points[:,3] = 1
    for index,xy in {11:(.4,.2),12:(.6,.2),23:(.43,.5),24:(.57,.5),27:(.43,.9),28:(.57,.9),13:(.35,.4),15:(.3,.5),14:(.65,.4),16:(.7,.5)}.items():
        points[index,:2] = xy
    result = ClothingEngine(catalog).render(frame,points,catalog.items[0],1)
    assert result.shape == frame.shape
    assert np.count_nonzero(result != frame) > 10000
    points[:,3] = 0
    np.testing.assert_array_equal(ClothingEngine(catalog).render(frame,points,catalog.items[0],1),frame)

def test_bad_asset_path(tmp_path):
    (tmp_path/'catalog.json').write_text(json.dumps([dict(id='x',gender='unisex',layers=[dict(asset='../escape.png')])]))
    with pytest.raises(ValueError,match='inside'):
        ClothingManager(tmp_path)

def test_photo_save_is_explicit(tmp_path):
    photo = prepare_photo(np.zeros((480,640,3),np.uint8))
    assert not list(tmp_path.iterdir())
    first = save_photo(photo,tmp_path)
    second = save_photo(photo,tmp_path)
    assert first != second and first.exists() and second.exists()
