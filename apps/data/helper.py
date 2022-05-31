from apps.data.models import *

def get_userprofileid_by_user_id(id):
    q = "SELECT *FROM data_userprofile WHERE user_id='" + str(id) + "'"
    profile = UserProfile.objects.raw(q)
    for p in profile:
        idz = p.id
    return idz
