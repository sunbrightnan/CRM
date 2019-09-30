from django.shortcuts import render,redirect,HttpResponse
from django.core.urlresolvers import reverse
from django.contrib import auth
from crm.forms import RegForm,CustomerForm,ConsultRecordForm,EnrollmentForm
from crm import models
from django.utils.safestring import mark_safe
from util.pagination import Pagination
from django.views.generic import View
from django.db.models import Q
from django.http import QueryDict
import copy
from django.db import transaction
from django.conf import settings


def login(request):
    errmsg = ''
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(username,password)
        obj = auth.authenticate(username=username,password=password)
        print(obj)
        if obj:
            auth.login(request,obj)
            return redirect('my_customer.html')
        errmsg = '用户名密码错误'

    return  render(request, 'login.html', {'errmsg': errmsg})


def register(request):
    form_obj = RegForm()
    if request.method == 'POST':
        # 校验参数
        form_obj = RegForm(request.POST)
        if form_obj.is_valid():
            # 创建新用户
            form_obj.cleaned_data.pop('re_password')
            models.UserProfile.objects.create_user(**form_obj.cleaned_data)

            # 方法二 form_obj.save()就能完成注册但是密码是明文，接受返回值单独设置密码
            # obj = form_obj.save()
            # obj.set_password(obj.password)
            # obj.save()

            return redirect('/login/')

    return render(request, 'reg.html', {'form_obj':form_obj})


# 客户列表 公户就是没有销售的
def customer_list(request):
    """
    展示客户列表
    :param request:
    :return:
    """
    # 拿客户数据
    if request.path_info == reverse('customer'):
        all_customer = models.Customer.objects.filter(consultant__isnull=True)
    else:
        all_customer = models.Customer.objects.filter(consultant=request.user)

    page = Pagination(request, all_customer.count())

    return render(request, 'crm/consultant/customer_list.html',
                  {"all_customer": all_customer[page.start:page.end], 'pagination': page.show_li})


# 客户列表cbv
class CustomerList(View):

    def get(self,request):

        # 调用下方的模糊搜索方法
        q = self.get_search_contion(['qq', 'name', 'last_consult_date'])

        if request.path_info == reverse('customer'):
            all_customer = models.Customer.objects.filter(q,consultant__isnull=True)
        else:
            all_customer = models.Customer.objects.filter(q,consultant=request.user)

        # query_params = copy.deepcopy(request.GET)  # <QueryDict: {'query': ['alex']}>
        query_params = request.GET.copy()  # <QueryDict: {'query': ['alex']}>
        # query=alex
        # print(request.GET.urlencode())

        # query_params['page'] = 1  # <QueryDict: {'query': ['alex'],'page': ['1']}>
        # print(request.GET.urlencode())  # query=alex&page=1
        page = Pagination(request, all_customer.count(),query_params,2)

        # 生成添加按钮
        add_btn,query_params = self.get_add_btn()

        return render(request, 'crm/consultant/customer_list.html',
                      {"all_customer": all_customer[page.start:page.end], 'pagination': page.show_li,'add_btn':add_btn,'query_params':query_params})

    def post(self,request):
        print(request.POST)

        action = request.POST.get('action')

        if not hasattr(self, action):
            return HttpResponse('非法操作')

        ret = getattr(self, action)()

        if ret:
            return ret

        return self.get(request)

    def multi_apply(self):
        # 公户变私户
        ids = self.request.POST.getlist('id')
        # 方法一
        #models.Customer.objects.filter(id__in=ids).update(consultant=self.request.user)

        # 方法二
        #self.request.user.customers.add(*models.Customer.objects.filter(id__in=ids))

        # return HttpResponse('申请成功')
        apply_num = len(ids)

        # 用户总总数不能超过设置值

        if self.request.user.customer.count() + apply_num > settings.CUSTOMER_MAX_NUM:
            return HttpResponse('每一个人不能超过设置值，给别人点机会')

        with transaction.atomic():
            # 事务 select_for_update加锁  为了防止两个销售同时加入一个客户出错
            obj_list = models.Customer.objects.filter(id__in = ids,consultant__isnumm=True).select_for_update()
            if apply_num == len(obj_list):
                obj_list.update(consultant=self.request.user)
            else:
                return HttpResponse('手速太慢')


    def multi_pub(self):
        # 私户变公户

        ids = self.request.POST.getlist('id')
        # 方法一
        models.Customer.objects.filter(id__in=ids).update(consultant=None)

        # 方法二
        #self.request.user.customers.remove(*models.Customer.objects.filter(id__in=ids))

    # 模糊搜索
    def get_search_contion(self, query_list):

        query = self.request.GET.get('query', '')

        q = Q()
        q.connector = 'OR'
        for i in query_list:
            q.children.append(Q(('{}__contains'.format(i), query)))

        return q

    def get_add_btn(self):
        # 获取添加按钮

        url = self.request.get_full_path()

        qd = QueryDict()
        qd._mutable = True
        qd['next'] = url
        # next=%2Fcrm%2Fcustomer_list%2F%3Fquery%3Dalex%26page%3D2
        query_params = qd.urlencode()

        # add_btn = '<a href="{}?next={}" class="btn btn-primary btn-sm">添加</a>'.format(reverse('add_customer'),url)
        add_btn = '<a href="{}?{}" class="btn btn-primary btn-sm">添加</a>'.format(reverse('add_customer'), query_params)

        return mark_safe(add_btn),query_params

users = [{'name': 'alex{}'.format(i), 'pwd': 'alexdsb{}'.format(i)} for i in range(1, 302)]


# def user_list(request):
#     # 当前页码
#     try:
#         current_page = int(request.GET.get('page', 1))
#         if current_page <= 0:
#             current_page = 1
#     except Exception as e:
#         current_page = 1
#     # 最多显示的页码数
#     max_show = 11
#     half_show = max_show // 2
#
#     # 每页显示的数据条数
#     per_num = 10
#     # 总数据量
#     all_count = len(users)
#
#     # 总页码数
#     total_num, more = divmod(all_count, per_num)
#     if more:
#         total_num += 1
#
#     # 总页码数小于最大显示数：显示总页码数
#     if total_num <= max_show:
#         page_start = 1
#         page_end = total_num
#     else:
#         # 总页码数大于最大显示数：最多显示11个
#         if current_page <= half_show:
#             page_start = 1
#             page_end = max_show
#         elif current_page + half_show >= total_num:
#             page_end = total_num
#             page_start = total_num - max_show + 1
#         else:
#             page_start = current_page - half_show
#             page_end = current_page + half_show
#     # 存放li标签的列表
#     html_list = []
#
#     first_li = '<li><a href="/user_list/?page=1">首页</a></li>'
#     html_list.append(first_li)
#
#     if current_page == 1:
#         prev_li = '<li class="disabled"><a><<</a></li>'
#     else:
#         prev_li = '<li><a href="/user_list/?page={0}"><<</a></li>'.format(current_page - 1)
#     html_list.append(prev_li)
#
#     for num in range(page_start, page_end + 1):
#         if current_page == num:
#             li_html = '<li class="active"><a href="/user_list/?page={0}">{0}</a></li>'.format(num)
#         else:
#             li_html = '<li><a href="/user_list/?page={0}">{0}</a></li>'.format(num)
#         html_list.append(li_html)
#
#     if current_page == total_num:
#         next_li = '<li class="disabled"><a>>></a></li>'
#     else:
#         next_li = '<li><a href="/user_list/?page={0}">>></a></li>'.format(current_page + 1)
#
#     html_list.append(next_li)
#
#     last_li = '<li><a href="/user_list/?page={}">尾页</a></li>'.format(total_num)
#     html_list.append(last_li)
#
#     html_str = mark_safe(''.join(html_list))
#
#     """
#     1   0  10
#     2  10  20
#     """
#     # 切片的起始值
#     start = (current_page - 1) * per_num
#     # 切片的终止值
#     end = current_page * per_num
#
#     return render(request, 'user_list.html',
#                   {
#                       "data": users[start:end],
#                       # 'total_num': range(page_start, page_end + 1)
#                       'html_str': html_str
#                   })


def user_list(request):
    page = Pagination(request, len(users))

    return render(request, 'user_list.html',
                  {
                      "data": users[page.start:page.end],
                      # 'total_num': range(page_start, page_end + 1)
                      'html_str': page.show_li
                  })


# 增加客户
def add_customer(request):

    # 实例化一个空的form对象
    form_obj = CustomerForm()

    if request.method == 'POST':
        # 实例化以恶个提交数据的form对象
        form_obj = CustomerForm(request.POST)
        # 对提交的数据进行校验
        if form_obj.is_valid():
            # 创建对象
            form_obj.save()
            return redirect(reverse('customer_list'))

    return render(request, 'crm/consultant/add_customer.html', {'form_obj':form_obj})


#编辑客户
def edit_customer(request,edit_id):
    # 根据id查出所需要需要编辑的客户对象
    obj = models.Customer.objects.filter(id=edit_id).first()

    form_obj = CustomerForm(instance=obj)
    if request.method == 'POST':
        # 将提交的数据和要修改的实例交给form对象
        form_obj = CustomerForm(request.POST,instance=obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(reverse('customer_list'))

    return render(request, 'crm/consultant/edit_customer.html', {'form_obj':form_obj})


# 新增和编辑何在一块
def customer(request,edit_id=None):
    # 根据id查出所需要需要编辑的客户对象
    obj = models.Customer.objects.filter(id=edit_id).first()

    form_obj = CustomerForm(instance=obj)
    if request.method == 'POST':
        # 将提交的数据和要修改的实例交给form对象
        form_obj = CustomerForm(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()

            # 获取到next
            next = request.GET.get('next')

            # return redirect(reverse('customer_list'))
            return redirect(next)

    return render(request, 'crm/consultant/edit_customer.html', {'form_obj': form_obj, 'edit_id':edit_id})

# 展示跟进记录
class ConsultRecord(View):

    def get(self, request, customer_id):

        if customer_id == '0':
            all_consult_record = models.ConsultRecord.objects.filter(delete_status=False,consultant=request.user)
        else:
            all_consult_record = models.ConsultRecord.objects.filter(customer_id=customer_id, delete_status=False)
        return render(request, 'crm/consultant/consult_record_list.html',
                      {
                          'all_consult_record': all_consult_record
                      })

def add_consult_record(request):
    obj = models.ConsultRecord(consultant=request.user)

    form_obj = ConsultRecordForm(instance=obj)
    if request.method == 'POST':
        form_obj = ConsultRecordForm(request.POST)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(reverse('consult_record',args=(0,)))

    return render(request, 'crm/consultant/add_consult_record.html', {'form_obj': form_obj})


# 编辑跟进记录
def edit_consult_record(request, edit_id):
    obj = models.ConsultRecord.objects.filter(id=edit_id).first()
    form_obj = ConsultRecordForm(instance=obj)
    if request.method == 'POST':
        form_obj = ConsultRecordForm(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(reverse('consult_record',args=(0,)))

    return render(request, 'crm/consultant/edit_consult_record.html', {'form_obj': form_obj})


# 展示报名记录
class EnrollmentList(View):

    def get(self, request, customer_id):

        if customer_id == '0':
            all_record = models.Enrollment.objects.filter(delete_status=False, customer__consultant=request.user)
        else:
            all_record = models.Enrollment.objects.filter(customer_id=customer_id, delete_status=False)

        # 获取搜索条件
        query_params = self.get_query_params()

        return render(request, 'crm/consultant/enrollment_list.html',
                      {
                          'all_record': all_record,
                          'query_params': query_params
                      })

    def get_query_params(self):
        # 获取添加按钮

        url = self.request.get_full_path()

        qd = QueryDict()
        qd._mutable = True
        qd['next'] = url
        query_params = qd.urlencode()

        return query_params

# 添加报名记录
def enrollment(request, customer_id=None, edit_id=None):
    obj = models.Enrollment.objects.filter(id=edit_id).first() or models.Enrollment(customer_id=customer_id)
    form_obj = EnrollmentForm(instance=obj)
    if request.method == 'POST':
        form_obj = EnrollmentForm(request.POST, instance=obj)
        if form_obj.is_valid():
            enrollment_obj = form_obj.save()
            # 修改客户的状态

            enrollment_obj.customer.status = 'signed'
            enrollment_obj.customer.save()

            next = request.GET.get('next')
            if next:
                return redirect(next)
            else:
                return redirect(reverse('my_customer'))

    return render(request, 'crm/consultant/enrollment.html', {"form_obj": form_obj})












