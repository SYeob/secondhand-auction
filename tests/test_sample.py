import requests

def test_site_is_alive():
    url = "https://syeob.lovable.app/"
    response = requests.get(url)
    
    assert response.status_code == 200