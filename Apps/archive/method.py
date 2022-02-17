from .models import Archive,get_archive_model
from files.models import get_ssfile_model


# 查找发放单，返回list
def archivefind(search, type):
    objs = get_archive_model(search, type)

    files = []
    for obj in objs:
        item = obj.to_dict()
        item['draw_num'] = get_ssfile_model(
            str(item['archive_id']), 'ARCHIVE_ID').count()
        if obj.bom:
            item['bom'] = 1

        files.append(item)

    return files



def can_edit_archive(obj, user):
    can_upbom = False
    can_upfile = False
    if obj.username == user.username:
        can_upfile = True

    if user.has_perm('archive.add_archivebom'):
        can_upbom = True

    return can_upfile, can_upbom
