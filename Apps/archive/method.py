from .models import Archive
from files.methods import get_ssfile_model

# 查找发放单模型，返回Obj
def get_archive_model(search, type):
    if search == 'ALL':
        q = Archive.objects.all()
    elif type == 'ARCHIVE_NO':
        q = Archive.objects.filter(archive_no__icontains=search)
    elif type == 'ARCHIVE_ID':
        q = Archive.objects.filter(archive_id__=search)
    elif type == 'PRODUCT_CODE':
        q = Archive.objects.filter(product__product_code__icontains=search)
    elif type == 'PRODUCT_NAME':
        q = Archive.objects.filter(product__product_name__icontains=search)
    elif type == 'USERNAME':
        q = Archive.objects.filter(username=search)
    elif type == 'DESC':
        q = Archive.objects.filter(description__icontains=search)
    else:
        q = []

    return q


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
