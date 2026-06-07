from app.services.travel_service import TravelService

if __name__ == '__main__':
    svc = TravelService()
    try:
        r = svc.delete_reservation(22)
        print('Deleted reservation rows:', r)
    except Exception as e:
        print('Delete reservation error:', e)

    try:
        v = svc.voyages.delete(3)
        print('Deleted voyage rows:', v)
    except Exception as e:
        print('Delete voyage error:', e)

    # verify
    try:
        rem = svc.database.fetch_one('SELECT COUNT(*) AS rem FROM reservations WHERE id_voyage = :v', {'v': 3})
        vr = svc.database.fetch_one('SELECT COUNT(*) AS vrem FROM voyages WHERE id_voyage = :v', {'v': 3})
        vp = svc.database.fetch_one('SELECT id_voyage, places_disponibles FROM voyages WHERE id_voyage = :v', {'v': 3})
        print('reservations_remaining:', rem['rem'] if rem else 0)
        print('voyage_remaining:', vr['vrem'] if vr else 0)
        print('voyage_places:', vp)
    except Exception as e:
        print('Verification error:', e)
